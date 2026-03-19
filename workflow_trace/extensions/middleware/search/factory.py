from workflow_trace.extensions.middleware.search.manager import SearchManager

_search_manager: SearchManager | None = None


def get_search_manager() -> SearchManager:
    global _search_manager
    if _search_manager is None:
        _search_manager = SearchManager()
    return _search_manager
