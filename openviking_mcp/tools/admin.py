# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""Admin tools: account and user management (ROOT/ADMIN only)."""

from __future__ import annotations

import json

from mcp.server.fastmcp import Context, FastMCP

from openviking.server.identity import Role
from openviking_cli.exceptions import OpenVikingError
from openviking_mcp.context import get_app, get_request_context
from openviking_mcp.errors import format_error, permission_denied


def _require_root(ctx: Context) -> str | None:
    """Return error JSON if caller is not ROOT, else None."""
    request_ctx = get_request_context(ctx)
    if request_ctx.role != Role.ROOT:
        return permission_denied("ROOT role required")
    return None


def _require_admin_or_root(ctx: Context, account_id: str) -> str | None:
    """Return error JSON if caller is not ROOT or ADMIN of the given account."""
    request_ctx = get_request_context(ctx)
    if request_ctx.role == Role.ROOT:
        return None
    if request_ctx.role == Role.ADMIN and request_ctx.user.account == account_id:
        return None
    return permission_denied("ROOT or account ADMIN role required")


def register_admin_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def admin_create_account(
        account_id: str, admin_user_id: str, ctx: Context = None
    ) -> str:
        """Create a new account (workspace) with its first admin user.

        Args:
            account_id: Unique account identifier
            admin_user_id: User ID for the initial admin user

        Returns ROOT role required.
        """
        try:
            if err := _require_root(ctx):
                return err
            app = get_app(ctx)
            if app.api_key_manager is None:
                return permission_denied("Auth not configured (dev mode)")
            request_ctx = get_request_context(ctx)
            user_key = await app.api_key_manager.create_account(
                account_id, admin_user_id
            )
            await app.service.initialize_account_directories(request_ctx)
            return json.dumps(
                {
                    "account_id": account_id,
                    "admin_user_id": admin_user_id,
                    "user_key": user_key,
                }
            )
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def admin_list_accounts(ctx: Context = None) -> str:
        """List all accounts. Requires ROOT role."""
        try:
            if err := _require_root(ctx):
                return err
            app = get_app(ctx)
            if app.api_key_manager is None:
                return permission_denied("Auth not configured (dev mode)")
            result = app.api_key_manager.get_accounts()
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def admin_delete_account(account_id: str, ctx: Context = None) -> str:
        """Delete an account and all its data. Requires ROOT role.

        Args:
            account_id: Account to delete
        """
        try:
            if err := _require_root(ctx):
                return err
            app = get_app(ctx)
            if app.api_key_manager is None:
                return permission_denied("Auth not configured (dev mode)")
            await app.api_key_manager.delete_account(account_id)
            return json.dumps({"account_id": account_id, "deleted": True})
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def admin_register_user(
        account_id: str,
        user_id: str,
        role: str = "user",
        ctx: Context = None,
    ) -> str:
        """Register a new user in an account. Requires ROOT or account ADMIN.

        Args:
            account_id: Target account
            user_id: New user ID
            role: User role ("user" or "admin")
        """
        try:
            if err := _require_admin_or_root(ctx, account_id):
                return err
            app = get_app(ctx)
            if app.api_key_manager is None:
                return permission_denied("Auth not configured (dev mode)")
            request_ctx = get_request_context(ctx)
            user_key = await app.api_key_manager.register_user(
                account_id, user_id, role
            )
            await app.service.initialize_user_directories(request_ctx)
            return json.dumps(
                {
                    "account_id": account_id,
                    "user_id": user_id,
                    "user_key": user_key,
                }
            )
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def admin_list_users(account_id: str, ctx: Context = None) -> str:
        """List all users in an account. Requires ROOT or account ADMIN.

        Args:
            account_id: Target account
        """
        try:
            if err := _require_admin_or_root(ctx, account_id):
                return err
            app = get_app(ctx)
            if app.api_key_manager is None:
                return permission_denied("Auth not configured (dev mode)")
            result = app.api_key_manager.get_users(account_id)
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def admin_remove_user(
        account_id: str, user_id: str, ctx: Context = None
    ) -> str:
        """Remove a user from an account. Requires ROOT or account ADMIN.

        Args:
            account_id: Target account
            user_id: User to remove
        """
        try:
            if err := _require_admin_or_root(ctx, account_id):
                return err
            app = get_app(ctx)
            if app.api_key_manager is None:
                return permission_denied("Auth not configured (dev mode)")
            await app.api_key_manager.remove_user(account_id, user_id)
            return json.dumps(
                {"account_id": account_id, "user_id": user_id, "deleted": True}
            )
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def admin_set_role(
        account_id: str, user_id: str, role: str, ctx: Context = None
    ) -> str:
        """Update a user's role. Requires ROOT role.

        Args:
            account_id: Target account
            user_id: Target user
            role: New role ("user" or "admin")
        """
        try:
            if err := _require_root(ctx):
                return err
            app = get_app(ctx)
            if app.api_key_manager is None:
                return permission_denied("Auth not configured (dev mode)")
            await app.api_key_manager.set_role(account_id, user_id, role)
            return json.dumps(
                {"account_id": account_id, "user_id": user_id, "role": role}
            )
        except OpenVikingError as e:
            return format_error(e)
