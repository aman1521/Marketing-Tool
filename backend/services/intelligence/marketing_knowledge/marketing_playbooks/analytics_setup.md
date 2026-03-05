# Analytics Setup

Proper tracking architectures map exactly to the company's funnel. Without clean tracking, AI operators guess blindly.

## Setup Phases

1. Core Pixel/Tag Initialization.
2. Standard Events (ViewContent, AddToCart, Purchase, Lead).
3. Custom Dimensions (user_type, plan_tier).
4. Cross-Domain Tracking.

## The Data Layer

Always push custom variables before the pixel fires via the `dataLayer` object so tracking platforms can consume rich context.

## Common Checks

- Did you verify standard UTM parameter capture (utm_source, utm_medium, utm_campaign)?
- Are overlapping GTM containers firing double pageviews?

## Output

- tracking_architecture_diagram
- event_schemas
