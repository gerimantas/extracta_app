"""Report query builder (Task 38).

Transforms a request dict into a parameterized SQL query over the transactions table.

Request shape:
{
  filters: {date_from?, date_to?, category_ids?[]},
  grouping: [field, ...],
  aggregations: [{field, func, alias}, ...]
}

Supported funcs: sum, count, avg
Supported group fields: month, year, category_id
"""
from __future__ import annotations

from typing import Any

ALLOWED_FUNCS = {"sum", "count", "avg"}
ALLOWED_GROUP_FIELDS = {"month", "year", "category_id"}


def build_report_query(request: dict[str, Any]) -> tuple[str, list[Any]]:
    filters = request.get("filters", {}) or {}
    grouping = request.get("grouping", []) or []
    aggregations = request.get("aggregations", []) or []

    if not aggregations:
        raise ValueError("At least one aggregation required")

    select_parts: list[str] = []
    group_fields: list[str] = []
    for g in grouping:
        if g not in ALLOWED_GROUP_FIELDS:
            raise ValueError(f"Unsupported group field: {g}")
        select_parts.append(g)
        group_fields.append(g)

    agg_selects: list[str] = []
    for agg in aggregations:
        field = agg["field"]
        func = agg["func"].lower()
        alias = agg.get("alias") or f"{func}_{field}"
        if func not in ALLOWED_FUNCS:
            raise ValueError(f"Unsupported aggregation function: {func}")
        func_sql = func.upper()
        if func == "count":
            # COUNT(field) or COUNT(*) maybe; keep simple
            agg_selects.append(f"COUNT({field}) AS {alias}")
        else:
            agg_selects.append(f"{func_sql}({field}) AS {alias}")
    select_clause = ", ".join(select_parts + agg_selects)

    sql = f"SELECT {select_clause} FROM transactions"

    where_clauses: list[str] = []
    params: list[Any] = []
    if "date_from" in filters:
        where_clauses.append("transaction_date >= ?")
        params.append(filters["date_from"])
    if "date_to" in filters:
        where_clauses.append("transaction_date <= ?")
        params.append(filters["date_to"])
    if "category_ids" in filters and filters["category_ids"]:
        ids = filters["category_ids"]
        placeholders = ",".join(["?"] * len(ids))
        where_clauses.append(f"category_id IN ({placeholders})")
        params.extend(ids)

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    if group_fields:
        sql += " GROUP BY " + ", ".join(group_fields)
        # Deterministic order: same as grouping
        sql += " ORDER BY " + ", ".join(group_fields)

    return sql, params

__all__ = ["build_report_query"]
