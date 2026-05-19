"""Clerk API client — search US federal court records."""
import base64
import json
from typing import Any
from urllib.parse import urlencode

try:
    import httpx
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


class ClerkError(Exception):
    """Raised when the Clerk API returns an error."""
    def __init__(self, message: str, status_code: int = 0, body: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body or {}


class PaymentRequired(ClerkError):
    """Raised when 402 Payment Required — need x402 USDC payment."""
    pass


class ClerkClient:
    """Client for the Clerk court records API.

    Usage (free/demo mode):
        client = ClerkClient()
        results = client.search("SEC v Ripple")

    Usage (with x402 payment):
        client = ClerkClient(tx_hash="0x...")
        results = client.search("SEC v Ripple")

    Args:
        base_url: API base URL (default: https://clerk.solvrlabs.ai)
        tx_hash: Transaction hash for x402 USDC payment on Base.
        payment_header: Raw x402 payment header (alternative to tx_hash).
    """

    def __init__(
        self,
        base_url: str = "https://clerk.solvrlabs.ai",
        tx_hash: str | None = None,
        payment_header: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self._payment_header = None

        if payment_header:
            self._payment_header = payment_header
        elif tx_hash:
            payload = json.dumps({"transaction": tx_hash})
            self._payment_header = base64.b64encode(payload.encode()).decode()

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self._payment_header:
            headers["X-PAYMENT"] = self._payment_header
        return headers

    def _handle_response(self, status: int, body: dict) -> dict:
        if status == 402:
            raise PaymentRequired(
                body.get("description", "Payment required"),
                status_code=402,
                body=body,
            )
        if status >= 400:
            raise ClerkError(
                body.get("error", f"HTTP {status}"),
                status_code=status,
                body=body,
            )
        return body

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        if params:
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            if params:
                url += "?" + urlencode(params)

        headers = self._headers()

        if _HAS_HTTPX:
            resp = httpx.get(url, headers=headers, timeout=30)
            try:
                body = resp.json()
            except Exception:
                raise ClerkError(f"HTTP {resp.status_code}: non-JSON response", status_code=resp.status_code)
            return self._handle_response(resp.status_code, body)
        elif _HAS_REQUESTS:
            resp = _requests.get(url, headers=headers, timeout=30)
            try:
                body = resp.json()
            except Exception:
                raise ClerkError(f"HTTP {resp.status_code}: non-JSON response", status_code=resp.status_code)
            return self._handle_response(resp.status_code, body)
        else:
            raise ImportError("Install httpx or requests: pip install httpx")

    # ── Public API ──────────────────────────────────────────────

    def search(
        self,
        query: str,
        court: str | None = None,
        date_after: str | None = None,
        date_before: str | None = None,
        limit: int = 20,
        source: str = "auto",
    ) -> list[dict[str, Any]]:
        """Search federal court cases.

        Args:
            query: Search query (party name, case name, or case number).
            court: Filter by court code (e.g. "cacd" for Central District of California).
            date_after: Filter cases filed after this date (YYYY-MM-DD).
            date_before: Filter cases filed before this date (YYYY-MM-DD).
            limit: Max results (1-50, default 20).
            source: Optional upstream routing hint. Defaults to "auto" (server selects the best upstream automatically).

        Returns:
            List of case dictionaries.
        """
        data = self._get("/search", {
            "q": query,
            "court": court,
            "date_after": date_after,
            "date_before": date_before,
            "limit": limit,
            "source": source,
        })
        return data.get("results", [])

    def docket(self, docket_id: str | int) -> dict[str, Any]:
        """Get full docket details.

        Args:
            docket_id: Numeric docket ID.

        Returns:
            Docket dictionary with parties, attorneys, and timeline.
        """
        data = self._get(f"/docket/{docket_id}")
        return data.get("docket", {})

    def parties(self, name: str, limit: int = 20) -> list[dict[str, Any]]:
        """Search for parties across all federal court dockets.

        Args:
            name: Party name to search for.
            limit: Max results (1-50, default 20).

        Returns:
            List of party dictionaries.
        """
        data = self._get("/parties", {"name": name, "limit": limit})
        return data.get("parties", [])

    def opinion(self, opinion_id: str | int) -> dict[str, Any]:
        """Get court opinion/document text.

        Args:
            opinion_id: Numeric opinion ID.

        Returns:
            Opinion dictionary with text, author, and case metadata.
        """
        data = self._get(f"/opinion/{opinion_id}")
        return data.get("opinion", {})

    def judges(self, name: str, limit: int = 20) -> list[dict[str, Any]]:
        """Search federal judges by name.

        Args:
            name: Judge name (last name) to search for.
            limit: Max results (1-50, default 20).

        Returns:
            List of judge dictionaries with appointment history.
        """
        data = self._get("/judges", {"name": name, "limit": limit})
        return data.get("judges", [])

    def filings(self, docket_id: str | int, limit: int = 50) -> list[dict[str, Any]]:
        """Get docket entries (filings) for a case.

        Args:
            docket_id: Numeric docket ID.
            limit: Max results (1-100, default 50).

        Returns:
            List of filing dictionaries with documents.
        """
        data = self._get(f"/filings/{docket_id}", {"limit": limit})
        return data.get("filings", [])

    def citations(
        self,
        query: str,
        court: str | None = None,
        date_after: str | None = None,
        date_before: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search court opinions by keyword, citation, or case name.

        Args:
            query: Search query (keyword, citation, or case name).
            court: Filter by court code (e.g. "scotus", "ca9").
            date_after: Filter opinions filed after this date (YYYY-MM-DD).
            date_before: Filter opinions filed before this date (YYYY-MM-DD).
            limit: Max results (1-50, default 20).

        Returns:
            List of opinion dictionaries.
        """
        data = self._get("/citations", {
            "q": query,
            "court": court,
            "date_after": date_after,
            "date_before": date_before,
            "limit": limit,
        })
        return data.get("opinions", [])

    def oral_arguments(
        self,
        query: str,
        court: str | None = None,
        date_after: str | None = None,
        date_before: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search oral argument recordings from federal courts.

        Args:
            query: Search query.
            court: Filter by court code.
            date_after: Filter arguments after this date (YYYY-MM-DD).
            date_before: Filter arguments before this date (YYYY-MM-DD).
            limit: Max results (1-50, default 20).

        Returns:
            List of oral argument dictionaries.
        """
        data = self._get("/oral-arguments", {
            "q": query,
            "court": court,
            "date_after": date_after,
            "date_before": date_before,
            "limit": limit,
        })
        return data.get("oral_arguments", [])

    def document(self, doc_id: str | int) -> dict[str, Any]:
        """Get a court document's metadata and download URL.

        Args:
            doc_id: Numeric document ID (from filings results).

        Returns:
            Document dictionary with download_url, plain_text, and metadata.
        """
        data = self._get(f"/document/{doc_id}")
        return data.get("document", {})

    def court(self, court_id: str) -> dict[str, Any]:
        """Get federal court metadata by court ID.

        Args:
            court_id: Court identifier (e.g. "cacd", "scotus", "ca9").

        Returns:
            Court dictionary with name, type, and jurisdiction info.
        """
        data = self._get(f"/court/{court_id}")
        return data.get("court", {})

    def health(self) -> dict[str, Any]:
        """Health check (free, no payment required)."""
        return self._get("/health")

    def info(self) -> dict[str, Any]:
        """Get API info and pricing."""
        return self._get("/")
