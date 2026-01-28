"""
API schema definitions for Gift Cards.
"""
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status

# Common response schemas
gift_card_response = {
    status.HTTP_200_OK: OpenApiResponse(
        response=OpenApiTypes.OBJECT,
        description="Gift card details",
        examples=[
            OpenApiExample(
                "Gift Card Response",
                value={
                    "id": 1,
                    "code": "GC12345678",
                    "initial_balance": "100.00",
                    "current_balance": "100.00",
                    "currency": "USD",
                    "gift_card_type": "digital",
                    "status": "active",
                    "expires_at": "2024-12-31T23:59:59Z",
                    "created_at": "2023-01-01T12:00:00Z",
                    "is_expired": False,
                    "is_redeemable": True,
                },
            )
        ],
    )
}

error_response = {
    status.HTTP_400_BAD_REQUEST: OpenApiResponse(
        response=OpenApiTypes.OBJECT,
        description="Bad Request",
        examples=[OpenApiExample("Error Response", value={"error": "Invalid input data"})],
    ),
    status.HTTP_404_NOT_FOUND: OpenApiResponse(
        response=OpenApiTypes.OBJECT,
        description="Not Found",
        examples=[OpenApiExample("Not Found", value={"error": "Gift card not found"})],
    ),
}

# Common parameters
gift_card_code_parameter = OpenApiParameter(
    name="code",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description="Gift card code",
    required=True,
)

# View schemas
gift_card_list_schema = extend_schema_view(
    list=extend_schema(
        summary="List all gift cards",
        description="Retrieve a paginated list of gift cards with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by status (active, redeemed, expired, voided)",
                enum=["active", "redeemed", "expired", "voided"],
            ),
            OpenApiParameter(
                name="gift_card_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by gift card type",
                enum=["digital", "physical", "promotional", "refund", "loyalty"],
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search in code, recipient_email, sender_email, recipient_name, sender_name",
            ),
        ],
        responses={**gift_card_response, **error_response},
    ),
    create=extend_schema(
        summary="Create a gift card",
        description="Create a new gift card with the specified details.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "initial_balance": {"type": "string", "format": "decimal", "example": "100.00"},
                    "currency": {"type": "string", "example": "USD"},
                    "gift_card_type": {
                        "type": "string",
                        "enum": ["digital", "physical", "promotional", "refund", "loyalty"],
                    },
                    "expires_at": {"type": "string", "format": "date-time", "nullable": True},
                    "recipient_email": {"type": "string", "format": "email", "nullable": True},
                    "recipient_name": {"type": "string", "nullable": True},
                    "sender_name": {"type": "string", "nullable": True},
                    "sender_email": {"type": "string", "format": "email", "nullable": True},
                    "message": {"type": "string", "nullable": True},
                },
                "required": ["initial_balance", "currency", "gift_card_type"],
            }
        },
        responses={
            status.HTTP_201_CREATED: gift_card_response[status.HTTP_200_OK],
            **error_response,
        },
    ),
)

gift_card_detail_schema = extend_schema_view(
    retrieve=extend_schema(
        summary="Retrieve a gift card",
        description="Get detailed information about a specific gift card.",
        responses={**gift_card_response, **error_response},
    ),
    update=extend_schema(
        summary="Update a gift card",
        description="Update an existing gift card.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "expires_at": {"type": "string", "format": "date-time", "nullable": True},
                    "recipient_email": {"type": "string", "format": "email", "nullable": True},
                    "recipient_name": {"type": "string", "nullable": True},
                    "sender_name": {"type": "string", "nullable": True},
                    "sender_email": {"type": "string", "format": "email", "nullable": True},
                    "message": {"type": "string", "nullable": True},
                    "metadata": {"type": "object", "nullable": True},
                },
            }
        },
        responses={**gift_card_response, **error_response},
    ),
    partial_update=extend_schema(
        summary="Partially update a gift card",
        description="Partially update an existing gift card.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "expires_at": {"type": "string", "format": "date-time", "nullable": True},
                    "recipient_email": {"type": "string", "format": "email", "nullable": True},
                    "recipient_name": {"type": "string", "nullable": True},
                    "sender_name": {"type": "string", "nullable": True},
                    "sender_email": {"type": "string", "format": "email", "nullable": True},
                    "message": {"type": "string", "nullable": True},
                    "metadata": {"type": "object", "nullable": True},
                },
            }
        },
        responses={**gift_card_response, **error_response},
    ),
    destroy=extend_schema(
        summary="Delete a gift card",
        description="Mark a gift card as deleted.",
        responses={status.HTTP_204_NO_CONTENT: None, **error_response},
    ),
)

gift_card_redeem_schema = extend_schema_view(
    redeem=extend_schema(
        summary="Redeem a gift card",
        description="Redeem an amount from a gift card.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "example": "GC12345678"},
                    "amount": {"type": "string", "format": "decimal", "example": "25.50"},
                    "order_id": {"type": "integer", "nullable": True},
                    "method": {
                        "type": "string",
                        "enum": ["online", "in_store"],
                        "default": "online",
                    },
                },
                "required": ["code", "amount"],
            }
        },
        responses={
            **gift_card_response,
            **error_response,
            status.HTTP_400_BAD_REQUEST: {
                "description": "Invalid redemption request",
                "examples": {"application/json": {"error": "Insufficient balance"}},
            },
        },
    )
)

gift_card_balance_schema = extend_schema_view(
    balance=extend_schema(
        summary="Check gift card balance",
        description="Get the current balance of a gift card.",
        parameters=[gift_card_code_parameter],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Gift card balance",
                examples=[
                    OpenApiExample(
                        "Balance Response",
                        value={
                            "code": "GC12345678",
                            "balance": "100.00",
                            "currency": "USD",
                            "is_expired": False,
                            "expires_at": "2024-12-31T23:59:59Z",
                        },
                    )
                ],
            ),
            **error_response,
        },
    )
)

gift_card_activate_schema = extend_schema_view(
    activate=extend_schema(
        summary="Activate a gift card",
        description="Activate an inactive gift card.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "expires_at": {"type": "string", "format": "date-time", "nullable": True},
                    "notes": {"type": "string", "nullable": True},
                },
            }
        },
        responses={**gift_card_response, **error_response},
    )
)

gift_card_void_schema = extend_schema_view(
    void=extend_schema(
        summary="Void a gift card",
        description="Void an active gift card.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string"},
                    "notes": {"type": "string", "nullable": True},
                },
                "required": ["reason"],
            }
        },
        responses={**gift_card_response, **error_response},
    )
)

# History schemas
gift_card_history_schema = extend_schema_view(
    list=extend_schema(
        summary="List gift card history",
        description="Retrieve history entries for gift cards with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="gift_card_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by gift card ID",
            ),
            OpenApiParameter(
                name="action",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by action type",
                enum=["created", "redeemed", "refunded", "expired", "voided", "activated"],
            ),
            OpenApiParameter(
                name="start_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by start date (YYYY-MM-DD)",
            ),
            OpenApiParameter(
                name="end_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by end date (YYYY-MM-DD)",
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a history entry",
        description="Get detailed information about a specific history entry.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="History entry details",
                examples=[
                    OpenApiExample(
                        "History Entry Response",
                        value={
                            "id": 1,
                            "action": "redeemed",
                            "amount": "25.50",
                            "created_at": "2023-01-01T12:00:00Z",
                            "notes": "Redeemed for order #123",
                            "metadata": {"order_id": "123", "method": "online"},
                        },
                    )
                ],
            ),
            **error_response,
        },
    ),
)

# Rate limiting information
rate_limit_info = """
## Rate Limiting

- **Balance checks**: 5 requests per minute
- **Redemptions**: 10 requests per minute
- **Other operations**: 30 requests per minute

When rate limited, the API will return a `429 Too Many Requests` response with a `Retry-After` header.
"""

# Main schema decorator
gift_card_schema = extend_schema(
    tags=["Gift Cards"],
    description=f"""
    Manage gift cards for your store.

    {rate_limit_info}

    ### Status Codes

    - `200 OK`: Request was successful
    - `201 Created`: Resource was created
    - `204 No Content`: Resource was deleted successfully
    - `400 Bad Request`: Invalid input data
    - `401 Unauthorized`: Authentication required
    - `403 Forbidden`: Insufficient permissions
    - `404 Not Found`: Resource not found
    - `429 Too Many Requests`: Rate limit exceeded
    """,
)
