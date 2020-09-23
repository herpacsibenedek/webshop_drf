Work in Progress

To be Done:
+ Tags model
+ Category model
+ Cart Model
+ Order Model
+ Address Model
+ Billing Profile Model
    - Shopfront/Catalog model



Ideas
+ Proxy Model for AttributeProduct/AttributeVariant
+ Proxy Model for ConnectedAttributeProduct/ConnectedAttributeVariant
    - This requires rewrite whole product/productvariant models as well
        - ProductVariant model same as Product, Product model has a field parent or main product which is a foreign key to self
+ drf-writable-nested
+ Nested serializer user its own create and update
+ product modified /created save mixin DRY
+ make serializers' foreign keys accepts int as id or instance which ever set



Testing: Way to go for 100%
+ Test for slug
    - not set or unchanged
    - maybe set model for editable:false

+ Test fields for Blank?, None?, and not set(missing)
    -  model level test
+ check status codes and exact valoidataion error

