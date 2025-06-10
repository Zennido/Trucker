import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def show_maintenance_management(data_manager):
    """Display maintenance management interface"""
    st.header("🔧 Maintenance Tracking")
    
    # Create tabs for different maintenance operations
    tab1, tab2, tab3 = st.tabs(["Add Maintenance Record", "Maintenance History", "Maintenance Alerts"])
    
    with tab1:
        show_add_maintenance_form(data_manager)
    
    with tab2:
        show_maintenance_history(data_manager)
    
    with tab3:
        show_maintenance_alerts(data_manager)

def show_add_maintenance_form(data_manager):
    """Form to add a new maintenance record"""
    st.subheader("Add Maintenance Record")
    
    vehicles = data_manager.get_vehicles()
    if not vehicles:
        st.warning("No vehicles found. Please add vehicles first.")
        return
    
    with st.form("add_maintenance_form"):
        # Vehicle selection
        vehicle_options = [f"{v['plate_number']} - {v['driver_name']}" for v in vehicles]
        selected_vehicle = st.selectbox("Select Vehicle*", vehicle_options)
        
        if selected_vehicle:
            plate_number = selected_vehicle.split(" - ")[0]
        
        # Date and basic info
        col1, col2 = st.columns(2)
        
        with col1:
            maintenance_date = st.date_input("Maintenance Date*", value=datetime.now().date())
            km_travelled = st.number_input("Current KM Reading*", min_value=0, step=1000)
            maintenance_type = st.selectbox("Maintenance Type", [
                "Routine Service", "Oil Change", "Filter Replacement", 
                "Tire Change", "Engine Repair", "Brake Service", "Other"
            ])
        
        with col2:
            next_service_km = st.number_input("Next Service KM", min_value=km_travelled, step=1000, value=km_travelled + 10000)
            mechanic_name = st.text_input("Mechanic/Service Center", placeholder="Enter mechanic or service center name")
            labor_cost = st.number_input("Labor Cost", min_value=0.0, step=100.0)
        
        # Engine Oil Section
        st.subheader("🛢️ Engine Oil")
        col3, col4 = st.columns(2)
        
        with col3:
            oil_changed = st.checkbox("Oil Changed")
            if oil_changed:
                oil_date = st.date_input("Oil Change Date", value=maintenance_date)
                oil_type = st.text_input("Oil Type", placeholder="e.g., 5W-30 Synthetic")
        
        with col4:
            if oil_changed:
                oil_expire_date = st.date_input("Next Oil Change Due", value=maintenance_date + timedelta(days=90))
                oil_cost = st.number_input("Oil Cost", min_value=0.0, step=50.0)
        
        # Air Filter Section
        st.subheader("🌪️ Air Filter")
        col5, col6 = st.columns(2)
        
        with col5:
            air_filter_changed = st.checkbox("Air Filter Changed")
            if air_filter_changed:
                filter_date = st.date_input("Filter Change Date", value=maintenance_date)
                filter_type = st.text_input("Filter Type", placeholder="e.g., High-flow air filter")
        
        with col6:
            if air_filter_changed:
                filter_expire_date = st.date_input("Next Filter Change Due", value=maintenance_date + timedelta(days=180))
                filter_cost = st.number_input("Filter Cost", min_value=0.0, step=25.0)
        
        # Diesel Section
        st.subheader("⛽ Diesel")
        col7, col8 = st.columns(2)
        
        with col7:
            diesel_added = st.number_input("Diesel Added (Liters)", min_value=0.0, step=10.0)
            diesel_cost_per_liter = st.number_input("Cost per Liter", min_value=0.0, step=0.1)
        
        with col8:
            fuel_efficiency = st.number_input("Fuel Efficiency (KM/L)", min_value=0.0, step=0.1)
            if diesel_added > 0:
                total_diesel_cost = diesel_added * diesel_cost_per_liter
                st.write(f"Total Diesel Cost: ${total_diesel_cost:.2f}")
        
        # Tires Section
        st.subheader("🛞 Tires")
        col9, col10 = st.columns(2)
        
        with col9:
            tires_changed = st.number_input("Number of Tires Changed", min_value=0, max_value=10, step=1)
            if tires_changed > 0:
                tire_brand = st.text_input("Tire Brand", placeholder="e.g., Michelin, Bridgestone")
                tire_size = st.text_input("Tire Size", placeholder="e.g., 295/80R22.5")
        
        with col10:
            if tires_changed > 0:
                tire_cost_each = st.number_input("Cost per Tire", min_value=0.0, step=50.0)
                total_tire_cost = tires_changed * tire_cost_each
                st.write(f"Total Tire Cost: ${total_tire_cost:.2f}")
        
        # Repair and Future Expenses
        st.subheader("💰 Expenses")
        col11, col12 = st.columns(2)
        
        with col11:
            repair_expense = st.number_input("Repair Expense", min_value=0.0, step=100.0)
            parts_cost = st.number_input("Parts Cost", min_value=0.0, step=50.0)
        
        with col12:
            future_expense = st.number_input("Estimated Future Expense", min_value=0.0, step=100.0)
            future_expense_description = st.text_area("Future Expense Description", placeholder="Describe upcoming maintenance needs")
        
        # Notes
        notes = st.text_area("Additional Notes", placeholder="Any additional notes about this maintenance")
        
        # Calculate total cost
        total_cost = (
            labor_cost + 
            (oil_cost if oil_changed else 0) + 
            (filter_cost if air_filter_changed else 0) + 
            (total_diesel_cost if diesel_added > 0 else 0) + 
            (total_tire_cost if tires_changed > 0 else 0) + 
            repair_expense + 
            parts_cost
        )
        
        st.write(f"**Total Maintenance Cost: ${total_cost:.2f}**")
        
        submitted = st.form_submit_button("Add Maintenance Record", type="primary")
        
        if submitted:
            if not selected_vehicle or km_travelled <= 0:
                st.error("Please select a vehicle and enter valid KM reading!")
            else:
                maintenance_data = {
                    'plate_number': plate_number,
                    'maintenance_date': maintenance_date.isoformat(),
                    'km_travelled': km_travelled,
                    'next_service_km': next_service_km,
                    'maintenance_type': maintenance_type,
                    'mechanic_name': mechanic_name,
                    'labor_cost': labor_cost,
                    'oil_changed': oil_changed,
                    'oil_date': oil_date.isoformat() if oil_changed else None,
                    'oil_type': oil_type if oil_changed else None,
                    'oil_expire_date': oil_expire_date.isoformat() if oil_changed else None,
                    'oil_cost': oil_cost if oil_changed else 0,
                    'air_filter_changed': air_filter_changed,
                    'filter_date': filter_date.isoformat() if air_filter_changed else None,
                    'filter_type': filter_type if air_filter_changed else None,
                    'filter_expire_date': filter_expire_date.isoformat() if air_filter_changed else None,
                    'filter_cost': filter_cost if air_filter_changed else 0,
                    'diesel_added': diesel_added,
                    'diesel_cost_per_liter': diesel_cost_per_liter,
                    'fuel_efficiency': fuel_efficiency,
                    'tires_changed': tires_changed,
                    'tire_brand': tire_brand if tires_changed > 0 else None,
                    'tire_size': tire_size if tires_changed > 0 else None,
                    'tire_cost_each': tire_cost_each if tires_changed > 0 else 0,
                    'repair_expense': repair_expense,
                    'parts_cost': parts_cost,
                    'future_expense': future_expense,
                    'future_expense_description': future_expense_description,
                    'notes': notes,
                    'total_cost': total_cost
                }
                
                success, message = data_manager.add_maintenance_record(maintenance_data)
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def show_maintenance_history(data_manager):
    """Display maintenance history"""
    st.subheader("Maintenance History")
    
    vehicles = data_manager.get_vehicles()
    maintenance_records = data_manager.get_maintenance_records()
    
    if not maintenance_records:
        st.info("No maintenance records found. Add your first maintenance record using the 'Add Maintenance Record' tab.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vehicle_filter = st.selectbox("Filter by Vehicle", ["All Vehicles"] + [v['plate_number'] for v in vehicles])
    
    with col2:
        maintenance_type_filter = st.selectbox("Filter by Type", ["All Types"] + list(set([r.get('maintenance_type', 'Unknown') for r in maintenance_records])))
    
    with col3:
        date_range = st.selectbox("Date Range", ["All Time", "Last 30 Days", "Last 90 Days", "Last Year"])
    
    # Apply filters
    filtered_records = maintenance_records
    
    if vehicle_filter != "All Vehicles":
        filtered_records = [r for r in filtered_records if r['plate_number'] == vehicle_filter]
    
    if maintenance_type_filter != "All Types":
        filtered_records = [r for r in filtered_records if r.get('maintenance_type') == maintenance_type_filter]
    
    if date_range != "All Time":
        days_map = {"Last 30 Days": 30, "Last 90 Days": 90, "Last Year": 365}
        cutoff_date = datetime.now() - timedelta(days=days_map[date_range])
        filtered_records = [
            r for r in filtered_records 
            if datetime.fromisoformat(r['maintenance_date']) >= cutoff_date
        ]
    
    # Sort by date (newest first)
    filtered_records.sort(key=lambda x: x['maintenance_date'], reverse=True)
    
    st.write(f"Found {len(filtered_records)} maintenance record(s)")
    
    # Display records
    for record in filtered_records:
        with st.expander(
            f"🔧 {record['plate_number']} - {record['maintenance_type']} ({record['maintenance_date']})",
            expanded=False
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Basic Information:**")
                st.write(f"Date: {record['maintenance_date']}")
                st.write(f"KM Reading: {record['km_travelled']:,}")
                st.write(f"Next Service: {record.get('next_service_km', 'N/A'):,} KM")
                st.write(f"Mechanic: {record.get('mechanic_name', 'N/A')}")
                
                if record.get('oil_changed'):
                    st.write("**🛢️ Oil Change:**")
                    st.write(f"Type: {record.get('oil_type', 'N/A')}")
                    st.write(f"Next Due: {record.get('oil_expire_date', 'N/A')}")
            
            with col2:
                if record.get('air_filter_changed'):
                    st.write("**🌪️ Air Filter:**")
                    st.write(f"Type: {record.get('filter_type', 'N/A')}")
                    st.write(f"Next Due: {record.get('filter_expire_date', 'N/A')}")
                
                if record.get('diesel_added', 0) > 0:
                    st.write("**⛽ Diesel:**")
                    st.write(f"Added: {record['diesel_added']} L")
                    st.write(f"Efficiency: {record.get('fuel_efficiency', 'N/A')} KM/L")
                
                if record.get('tires_changed', 0) > 0:
                    st.write("**🛞 Tires:**")
                    st.write(f"Changed: {record['tires_changed']} tires")
                    st.write(f"Brand: {record.get('tire_brand', 'N/A')}")
            
            with col3:
                st.write("**💰 Costs:**")
                st.write(f"Labor: ${record.get('labor_cost', 0):.2f}")
                st.write(f"Oil: ${record.get('oil_cost', 0):.2f}")
                st.write(f"Filter: ${record.get('filter_cost', 0):.2f}")
                st.write(f"Repairs: ${record.get('repair_expense', 0):.2f}")
                st.write(f"Parts: ${record.get('parts_cost', 0):.2f}")
                st.write(f"**Total: ${record.get('total_cost', 0):.2f}**")
                
                if record.get('future_expense', 0) > 0:
                    st.write(f"Future: ${record['future_expense']:.2f}")
            
            if record.get('notes'):
                st.write("**Notes:**")
                st.write(record['notes'])
    
    # Summary statistics
    if filtered_records:
        st.subheader("Maintenance Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_records = len(filtered_records)
            st.metric("Total Records", total_records)
        
        with col2:
            total_cost = sum([r.get('total_cost', 0) for r in filtered_records])
            st.metric("Total Cost", f"${total_cost:,.2f}")
        
        with col3:
            avg_cost = total_cost / total_records if total_records > 0 else 0
            st.metric("Average Cost", f"${avg_cost:.2f}")
        
        with col4:
            oil_changes = len([r for r in filtered_records if r.get('oil_changed')])
            st.metric("Oil Changes", oil_changes)

def show_maintenance_alerts(data_manager):
    """Display maintenance alerts and upcoming schedules"""
    st.subheader("Maintenance Alerts")
    
    # Get maintenance alerts
    alerts = data_manager.get_maintenance_alerts()
    
    if alerts:
        st.error(f"⚠️ {len(alerts)} maintenance alert(s) found!")
        
        for alert in alerts:
            st.warning(f"🚛 {alert['plate_number']}: {alert['alert_type']} (Priority: {alert['priority']})")
    else:
        st.success("✅ No maintenance alerts at this time.")
    
    # Upcoming maintenance schedule
    st.subheader("Upcoming Maintenance Schedule")
    
    vehicles = data_manager.get_vehicles()
    maintenance_records = data_manager.get_maintenance_records()
    
    upcoming_maintenance = []
    
    for vehicle in vehicles:
        plate = vehicle['plate_number']
        vehicle_maintenance = [m for m in maintenance_records if m['plate_number'] == plate]
        
        if not vehicle_maintenance:
            continue
        
        # Get latest maintenance
        latest_maintenance = max(vehicle_maintenance, key=lambda x: x['created_at'])
        
        # Check for upcoming oil change
        if latest_maintenance.get('oil_expire_date'):
            oil_due = datetime.fromisoformat(latest_maintenance['oil_expire_date'])
            days_until_oil = (oil_due - datetime.now()).days
            
            if days_until_oil <= 30:
                upcoming_maintenance.append({
                    'plate_number': plate,
                    'maintenance_type': 'Oil Change',
                    'due_date': oil_due.strftime("%Y-%m-%d"),
                    'days_remaining': days_until_oil,
                    'priority': 'High' if days_until_oil <= 7 else 'Medium'
                })
        
        # Check for upcoming filter change
        if latest_maintenance.get('filter_expire_date'):
            filter_due = datetime.fromisoformat(latest_maintenance['filter_expire_date'])
            days_until_filter = (filter_due - datetime.now()).days
            
            if days_until_filter <= 60:
                upcoming_maintenance.append({
                    'plate_number': plate,
                    'maintenance_type': 'Air Filter Change',
                    'due_date': filter_due.strftime("%Y-%m-%d"),
                    'days_remaining': days_until_filter,
                    'priority': 'High' if days_until_filter <= 14 else 'Low'
                })
        
        # Check for service based on KM
        current_km = latest_maintenance.get('km_travelled', 0)
        next_service_km = latest_maintenance.get('next_service_km', current_km + 10000)
        
        if current_km >= next_service_km * 0.9:  # 90% of service interval
            upcoming_maintenance.append({
                'plate_number': plate,
                'maintenance_type': 'Routine Service',
                'due_date': 'Based on KM',
                'days_remaining': 'Soon',
                'priority': 'High' if current_km >= next_service_km else 'Medium'
            })
    
    if upcoming_maintenance:
        # Sort by priority and days remaining
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        upcoming_maintenance.sort(key=lambda x: (priority_order.get(x['priority'], 3), x.get('days_remaining', 999)))
        
        for item in upcoming_maintenance:
            priority_color = {
                'High': '🔴',
                'Medium': '🟡', 
                'Low': '🟢'
            }.get(item['priority'], '⚫')
            
            st.info(f"{priority_color} **{item['plate_number']}** - {item['maintenance_type']} due {item['due_date']} ({item['days_remaining']} days)")
    else:
        st.success("✅ No upcoming maintenance scheduled.")
    
    # Maintenance statistics
    st.subheader("Maintenance Statistics")
    
    if maintenance_records:
        # Create a DataFrame for analysis
        df = pd.DataFrame(maintenance_records)
        df['maintenance_date'] = pd.to_datetime(df['maintenance_date'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Maintenance frequency by vehicle
            maintenance_by_vehicle = df.groupby('plate_number').size().reset_index(name='count')
            st.write("**Maintenance Frequency by Vehicle:**")
            st.dataframe(maintenance_by_vehicle, hide_index=True)
        
        with col2:
            # Cost analysis by maintenance type
            cost_by_type = df.groupby('maintenance_type')['total_cost'].sum().reset_index()
            cost_by_type = cost_by_type.sort_values('total_cost', ascending=False)
            st.write("**Cost by Maintenance Type:**")
            st.dataframe(cost_by_type, hide_index=True)
