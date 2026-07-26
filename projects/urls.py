"""MCP transport URLs."""

from django.urls import path

from .views import mcp_endpoint

urlpatterns = [path("", mcp_endpoint, name="mcp-endpoint")]
