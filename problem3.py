@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):

    try:
        alerts = []

        RECENT_DAYS = 30  # considering last 30 days as recent activity

        products = Product.query.filter_by(company_id=company_id).all()

        for product in products:
            
            # checking recent sales activity for this product
            recent_sales = Sales.query.filter(
                Sales.product_id == product.id,
                Sales.created_at >= datetime.utcnow() - timedelta(days=RECENT_DAYS)
            ).count()

            if recent_sales == 0:
                continue
            
            # getting threshold (default if not set)
            threshold = getattr(product, 'low_stock_threshold', 10)
            inventories = Inventory.query.filter_by(product_id=product.id).all()

            for inv in inventories:
                
                # checking if stock is below threshold
                if inv.quantity < threshold:
                    avg_daily_sales = max(recent_sales / RECENT_DAYS, 1)
                    days_until_stockout = int(inv.quantity / avg_daily_sales)
                    # fetching supplier info
                    supplier = SupplierProduct.query.filter_by(product_id=product.id).first()
                    supplier_data = None
                    if supplier:
                        supplier_data = {
                            "id": supplier.supplier.id,
                            "name": supplier.supplier.name,
                            "contact_email": getattr(supplier.supplier, 'email', None)
                        }
                    # preparing alert response
                    alerts.append({
                        "product_id": product.id,
                        "product_name": product.name,
                        "sku": product.sku,
                        "warehouse_id": inv.warehouse_id,
                        "warehouse_name": Warehouse.query.get(inv.warehouse_id).name,
                        "current_stock": inv.quantity,
                        "threshold": threshold,
                        "days_until_stockout": days_until_stockout,
                        "supplier": supplier_data
                    })

        return jsonify({
            "alerts": alerts,
            "total_alerts": len(alerts)
        }), 200

    except Exception as e:
        logger.error(f"error in low stock alerts: {e}", exc_info=True)
        return jsonify({"error": "failed to fetch alerts"}), 500