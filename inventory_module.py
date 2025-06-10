import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def show_inventory_management(data_manager):
    """Display inventory management interface"""
    st.header("📦 Inventory Management")
    
    # Create tabs for different inventory operations
    tab1, tab2, tab3 = st.tabs(["Current Stock", "Stock Movements", "Low Stock Alerts"])
    
    with tab1:
        show_current_stock(data_manager)
    
    with tab2:
        show_stock_movements(data_manager)
    
    with tab3:
        show_low_stock_alerts(data_manager)

def show_current_stock(data_manager):
    """Display current inventory levels and allow stock updates"""
    st.subheader("Current Stock Levels")
    
    inventory = data_manager.get_inventory()
    
    # Display current stock in cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🛢️ Engine Oil",
            value=f"{inventory['oil']} units",
            help="Number of oil containers in stock"
        )
    
    with col2:
        st.metric(
            label="🌪️ Air Filters", 
            value=f"{inventory['air_filter']} units",
            help="Number of air filters in stock"
        )
    
    with col3:
        st.metric(
            label="🛞 Tires",
            value=f"{inventory['tires']} units", 
            help="Number of tires in stock"
        )
    
    # Stock management forms
    st.subheader("Stock Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Add Stock**")
        with st.form("add_stock_form"):
            item_type = st.selectbox("Item Type", ["oil", "air_filter", "tires"])
            quantity = st.number_input("Quantity to Add", min_value=1, step=1)
            cost_per_unit = st.number_input("Cost per Unit", min_value=0.0, step=1.0)
            supplier = st.text_input("Supplier", placeholder="Enter supplier name")
            purchase_date = st.date_input("Purchase Date", value=datetime.now().date())
            notes = st.text_area("Notes", placeholder="Any additional notes about this purchase")
            
            add_submitted = st.form_submit_button("Add to Stock", type="primary")
            
            if add_submitted:
                success, message = data_manager.update_inventory(item_type, quantity, 'add')
                if success:
                    # Log the stock movement (you could expand this to track movements)
                    st.success(f"Added {quantity} {item_type.replace('_', ' ')} to stock")
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        st.write("**Remove Stock**")
        with st.form("remove_stock_form"):
            item_type_remove = st.selectbox("Item Type", ["oil", "air_filter", "tires"], key="remove_item")
            quantity_remove = st.number_input("Quantity to Remove", min_value=1, step=1, key="remove_qty")
            reason = st.selectbox("Reason", ["Used in Maintenance", "Damaged", "Expired", "Other"])
            reason_notes = st.text_area("Reason Details", placeholder="Additional details about removal")
            
            remove_submitted = st.form_submit_button("Remove from Stock", type="secondary")
            
            if remove_submitted:
                current_stock = inventory[item_type_remove]
                if quantity_remove > current_stock:
                    st.error(f"Cannot remove {quantity_remove} {item_type_remove.replace('_', ' ')}. Only {current_stock} available.")
                else:
                    success, message = data_manager.update_inventory(item_type_remove, quantity_remove, 'subtract')
                    if success:
                        st.success(f"Removed {quantity_remove} {item_type_remove.replace('_', ' ')} from stock")
                        st.rerun()
                    else:
                        st.error(message)
    
    # Inventory valuation (if you want to track costs)
    st.subheader("Inventory Overview")
    
    # Create a simple inventory summary table
    inventory_data = []
    item_names = {
        'oil': '🛢️ Engine Oil',
        'air_filter': '🌪️ Air Filters', 
        'tires': '🛞 Tires'
    }
    
    for item_key, item_name in item_names.items():
        quantity = inventory[item_key]
        status = "Low Stock" if quantity < 5 else "In Stock" if quantity < 20 else "Well Stocked"
        status_color = "🔴" if quantity < 5 else "🟡" if quantity < 20 else "🟢"
        
        inventory_data.append({
            'Item': item_name,
            'Quantity': quantity,
            'Status': f"{status_color} {status}",
            'Reorder Level': get_reorder_level(item_key),
            'Max Capacity': get_max_capacity(item_key)
        })
    
    df_inventory = pd.DataFrame(inventory_data)
    st.dataframe(df_inventory, hide_index=True, use_container_width=True)
    
    # Quick stock actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🛒 Generate Purchase Order", help="Generate a purchase order for low stock items"):
            low_stock_items = []
            for item_key, quantity in inventory.items():
                if quantity < get_reorder_level(item_key):
                    low_stock_items.append({
                        'item': item_key.replace('_', ' ').title(),
                        'current_stock': quantity,
                        'reorder_level': get_reorder_level(item_key),
                        'suggested_order': get_reorder_level(item_key) * 2 - quantity
                    })
            
            if low_stock_items:
                st.write("**Purchase Order Suggestion:**")
                for item in low_stock_items:
                    st.write(f"- {item['item']}: Order {item['suggested_order']} units (Current: {item['current_stock']}, Reorder at: {item['reorder_level']})")
            else:
                st.success("All items are well stocked!")
    
    with col2:
        if st.button("📊 Export Inventory Report"):
            # Create a downloadable CSV
            df_export = pd.DataFrame([inventory])
            df_export['generated_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"inventory_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("🔄 Reset Stock Levels", help="Reset all stock levels (use with caution)"):
            st.warning("This action will reset all stock levels to zero. This cannot be undone.")
            if st.button("Confirm Reset", type="secondary"):
                reset_inventory = {'oil': 0, 'air_filter': 0, 'tires': 0}
                data_manager.save_data('inventory', reset_inventory)
                st.success("Inventory reset successfully")
                st.rerun()

def show_stock_movements(data_manager):
    """Display stock movement history and trends"""
    st.subheader("Stock Movement History")
    
    # Get maintenance records to show stock usage
    maintenance_records = data_manager.get_maintenance_records()
    
    if not maintenance_records:
        st.info("No stock movements recorded yet. Stock movements are tracked when maintenance records are added.")
        return
    
    # Extract stock movements from maintenance records
    stock_movements = []
    
    for record in maintenance_records:
        if record.get('oil_changed'):
            stock_movements.append({
                'date': record['maintenance_date'],
                'item': 'Engine Oil',
                'quantity': -1,  # Negative for usage
                'type': 'Usage',
                'vehicle': record['plate_number'],
                'reference': f"Maintenance - {record.get('maintenance_type', 'N/A')}"
            })
        
        if record.get('air_filter_changed'):
            stock_movements.append({
                'date': record['maintenance_date'],
                'item': 'Air Filter',
                'quantity': -1,
                'type': 'Usage',
                'vehicle': record['plate_number'],
                'reference': f"Maintenance - {record.get('maintenance_type', 'N/A')}"
            })
        
        if record.get('tires_changed', 0) > 0:
            stock_movements.append({
                'date': record['maintenance_date'],
                'item': 'Tires',
                'quantity': -record['tires_changed'],
                'type': 'Usage',
                'vehicle': record['plate_number'],
                'reference': f"Maintenance - {record.get('maintenance_type', 'N/A')}"
            })
    
    if stock_movements:
        # Sort by date (newest first)
        stock_movements.sort(key=lambda x: x['date'], reverse=True)
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            item_filter = st.selectbox("Filter by Item", ["All Items"] + list(set([m['item'] for m in stock_movements])))
        
        with col2:
            type_filter = st.selectbox("Filter by Type", ["All Types", "Usage", "Addition", "Removal"])
        
        with col3:
            vehicle_filter = st.selectbox("Filter by Vehicle", ["All Vehicles"] + list(set([m['vehicle'] for m in stock_movements if m['vehicle']])))
        
        # Apply filters
        filtered_movements = stock_movements
        
        if item_filter != "All Items":
            filtered_movements = [m for m in filtered_movements if m['item'] == item_filter]
        
        if type_filter != "All Types":
            filtered_movements = [m for m in filtered_movements if m['type'] == type_filter]
        
        if vehicle_filter != "All Vehicles":
            filtered_movements = [m for m in filtered_movements if m['vehicle'] == vehicle_filter]
        
        # Display movements
        st.write(f"Found {len(filtered_movements)} stock movement(s)")
        
        for movement in filtered_movements[:20]:  # Show last 20 movements
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{movement['date']}**")
                st.write(movement['item'])
            
            with col2:
                qty_color = "🔴" if movement['quantity'] < 0 else "🟢"
                st.write(f"{qty_color} {movement['quantity']:+d}")
                st.write(movement['type'])
            
            with col3:
                st.write(f"🚛 {movement['vehicle']}")
            
            with col4:
                st.write(movement['reference'])
        
        # Movement statistics
        st.subheader("Usage Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Usage by item type
            item_usage = {}
            for movement in stock_movements:
                if movement['quantity'] < 0:  # Only count usage (negative quantities)
                    item = movement['item']
                    item_usage[item] = item_usage.get(item, 0) + abs(movement['quantity'])
            
            if item_usage:
                st.write("**Total Usage by Item:**")
                for item, usage in item_usage.items():
                    st.write(f"- {item}: {usage} units")
        
        with col2:
            # Usage by vehicle
            vehicle_usage = {}
            for movement in stock_movements:
                if movement['quantity'] < 0:
                    vehicle = movement['vehicle']
                    vehicle_usage[vehicle] = vehicle_usage.get(vehicle, 0) + abs(movement['quantity'])
            
            if vehicle_usage:
                st.write("**Total Usage by Vehicle:**")
                sorted_vehicles = sorted(vehicle_usage.items(), key=lambda x: x[1], reverse=True)
                for vehicle, usage in sorted_vehicles[:5]:  # Top 5
                    st.write(f"- {vehicle}: {usage} items")
    
    else:
        st.info("No stock movements recorded yet.")

def show_low_stock_alerts(data_manager):
    """Display low stock alerts and recommendations"""
    st.subheader("Low Stock Alerts")
    
    inventory = data_manager.get_inventory()
    
    # Define reorder levels and check for low stock
    low_stock_items = []
    
    for item_key, quantity in inventory.items():
        reorder_level = get_reorder_level(item_key)
        if quantity <= reorder_level:
            item_name = item_key.replace('_', ' ').title()
            priority = "Critical" if quantity == 0 else "High" if quantity <= reorder_level * 0.5 else "Medium"
            
            low_stock_items.append({
                'item': item_name,
                'current_stock': quantity,
                'reorder_level': reorder_level,
                'priority': priority,
                'recommended_order': max(reorder_level * 2 - quantity, reorder_level)
            })
    
    if low_stock_items:
        st.error(f"⚠️ {len(low_stock_items)} item(s) need restocking!")
        
        for item in low_stock_items:
            priority_color = {
                'Critical': '🔴',
                'High': '🟡',
                'Medium': '🟠'
            }.get(item['priority'], '⚫')
            
            with st.expander(f"{priority_color} {item['item']} - {item['priority']} Priority", expanded=item['priority'] == 'Critical'):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Current Stock:** {item['current_stock']} units")
                    st.write(f"**Reorder Level:** {item['reorder_level']} units")
                    st.write(f"**Priority:** {item['priority']}")
                
                with col2:
                    st.write(f"**Recommended Order:** {item['recommended_order']} units")
                    
                    if st.button(f"Quick Restock {item['item']}", key=f"restock_{item['item']}"):
                        # Quick restock to recommended level
                        success, message = data_manager.update_inventory(
                            item['item'].lower().replace(' ', '_'), 
                            item['recommended_order'], 
                            'add'
                        )
                        if success:
                            st.success(f"Added {item['recommended_order']} {item['item']} to stock")
                            st.rerun()
    else:
        st.success("✅ All items are adequately stocked!")
    
    # Restocking recommendations based on usage patterns
    st.subheader("Restocking Recommendations")
    
    maintenance_records = data_manager.get_maintenance_records()
    
    if maintenance_records:
        # Calculate usage rate (items used per month)
        recent_records = [
            r for r in maintenance_records 
            if datetime.fromisoformat(r['maintenance_date']) >= datetime.now() - timedelta(days=90)
        ]
        
        if recent_records:
            oil_usage = len([r for r in recent_records if r.get('oil_changed')])
            filter_usage = len([r for r in recent_records if r.get('air_filter_changed')])
            tire_usage = sum([r.get('tires_changed', 0) for r in recent_records])
            
            # Calculate monthly usage rate
            months = 3  # Looking at last 3 months
            oil_monthly = oil_usage / months
            filter_monthly = filter_usage / months
            tire_monthly = tire_usage / months
            
            st.write("**Usage Analysis (Last 3 Months):**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Oil Usage", f"{oil_usage} units", f"{oil_monthly:.1f}/month")
                projected_oil_need = int(oil_monthly * 6)  # 6 months projection
                st.write(f"6-month projection: {projected_oil_need} units")
            
            with col2:
                st.metric("Filter Usage", f"{filter_usage} units", f"{filter_monthly:.1f}/month")
                projected_filter_need = int(filter_monthly * 6)
                st.write(f"6-month projection: {projected_filter_need} units")
            
            with col3:
                st.metric("Tire Usage", f"{tire_usage} units", f"{tire_monthly:.1f}/month")
                projected_tire_need = int(tire_monthly * 6)
                st.write(f"6-month projection: {projected_tire_need} units")
            
            # Seasonal recommendations
            st.write("**Seasonal Recommendations:**")
            current_month = datetime.now().month
            
            if current_month in [11, 12, 1, 2]:  # Winter months
                st.info("❄️ Winter Season: Consider stocking up on winter-grade oil and additional tire replacements due to harsh conditions.")
            elif current_month in [6, 7, 8]:  # Summer months
                st.info("☀️ Summer Season: High usage period. Ensure adequate air filter stock due to dust and increased operations.")
            else:
                st.info("🔄 Regular Season: Maintain standard stock levels based on usage patterns.")
    
    # Cost optimization suggestions
    st.subheader("Cost Optimization")
    
    st.write("**Bulk Purchase Opportunities:**")
    
    suggestions = [
        "Consider bulk purchasing oil when stock drops below 10 units for better pricing",
        "Air filters have longer shelf life - consider quarterly bulk orders",
        "Tire purchases: Negotiate better rates for orders of 20+ units",
        "Track seasonal price fluctuations for optimal purchasing timing"
    ]
    
    for suggestion in suggestions:
        st.write(f"💡 {suggestion}")

def get_reorder_level(item_type):
    """Get reorder level for different item types"""
    reorder_levels = {
        'oil': 5,
        'air_filter': 10, 
        'tires': 8
    }
    return reorder_levels.get(item_type, 5)

def get_max_capacity(item_type):
    """Get maximum storage capacity for different item types"""
    max_capacities = {
        'oil': 50,
        'air_filter': 100,
        'tires': 40
    }
    return max_capacities.get(item_type, 50)
