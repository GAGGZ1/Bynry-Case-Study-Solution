@app.route('/api/products', methods=['POST'])
def create_product():

    data = request.get_json(silent=True)  # ensuring the JSON body exists before processing
    if not data:
        return jsonify({"error": "Invalid request: JSON body is required."}), 400

    required_fields = ['name', 'sku', 'price', 'warehouse_id']  # must check required fields
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400


    try:
        price = Decimal(str(data['price']))  # price can come in different formats, so validating it
        if price < 0:
            return jsonify({"error": "Invalid price: must be a non-negative value."}), 400
    except InvalidOperation:
        return jsonify({"error": f"Invalid price format: {data['price']!r}"}), 400


    try:
        initial_quantity = int(data.get('initial_quantity', 0))
        if initial_quantity < 0:  # checking the quantity
            return jsonify({"error": "Invalid initial_quantity: must be non-negative."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid initial_quantity: must be an integer."}), 400

    try:
     
        product = Product(
            name=data['name'].strip(),
            sku=data['sku'].strip().upper(),
            price=price,
            description=data.get('description', None)
        )
        db.session.add(product)
        db.session.flush()  # avoid duplicate commits and get product.id before commit

       
        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data['warehouse_id'],
            quantity=initial_quantity
        )
        db.session.add(inventory)

     
        db.session.commit()  # using a single commit to ensure atomic operation

        return jsonify({
            "message": "Product created successfully.",
            "product_id": product.id,
            "sku": product.sku,
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Duplicate SKU: product with this SKU already exists."}), 409

    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"error": "Unexpected server error. Please try again later."}), 500
