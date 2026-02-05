"""
Core package for the Project Chimera codebase.

This package will eventually host the runtime implementation used by
skills and agents, e.g. modules like:

- project_chimera.skills.trend_fetcher
- project_chimera.skills.content_generator

For now it exists primarily so that the project can be installed
as an editable package without setuptools trying to auto-discover
documentation and spec directories as top-level packages.
"""

__all__: list[str] = []

