from marshmallow import Schema, fields, validate


class ProductCreateSchema(Schema):
    sku = fields.String(required=True, validate=validate.Length(min=3, max=32))
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    price_cents = fields.Integer(required=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Integer(load_default=0, validate=validate.Range(min=0))


class ProductUpdateSchema(Schema):
    sku = fields.String(validate=validate.Length(min=3, max=32))
    name = fields.String(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    price_cents = fields.Integer(validate=validate.Range(min=0))
    qty_in_stock = fields.Integer(validate=validate.Range(min=0))

class ReserveSchema(Schema):
    qty = fields.Integer(required=True, validate=validate.Range(min=1))
