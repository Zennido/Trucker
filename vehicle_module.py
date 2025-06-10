import streamlit as st
import pandas as pd
from datetime import datetime

def show_vehicle_management(data_manager):
    """Display vehicle management interface"""
    st.header("🚛 Vehicle Management")
    
    # Create tabs for different vehicle operations
    tab1, tab2, tab3 = st.tabs(["Add New Vehicle", "View Fleet", "Edit Vehicle"])
    
    with tab1:
        show_add_vehicle_form(data_manager)
    
    with tab2:
        show_vehicle_list(data_manager)
    
    with tab3:
        show_edit_vehicle_form(data_manager)

def show_add_vehicle_form(data_manager):
    """Form to add a new vehicle"""
    st.subheader("Add New Vehicle")
    
    with st.form("add_vehicle_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            plate_number = st.text_input("Plate Number*", placeholder="e.g., ABC-123")
            driver_name = st.text_input("Driver Name*", placeholder="Enter driver's full name")
            helper_name = st.text_input("Helper Name", placeholder="Enter helper's name (optional)")
        
        with col2:
            tanker_size = st.number_input("Tanker Size (Liters)", min_value=0, value=0, step=100)
            vehicle_type = st.selectbox("Vehicle Type", ["Tanker", "Container", "Flatbed", "Box Truck", "Other"])
        
        # Route permits selection
        st.subheader("Route Permits")
        permits = data_manager.get_permits()
        available_permits = [f"{p['permit_number']} - {p['location']}" for p in permits]
        
        if available_permits:
            selected_permits = st.multiselect(
                "Select Route Permits (multiple allowed)",
                available_permits,
                help="You can select multiple permits for this vehicle"
            )
        else:
            st.info("No permits available. Add permits first in the Permits & Tax section.")
            selected_permits = []
        
        # Additional details
        st.subheader("Additional Information")
        col3, col4 = st.columns(2)
        
        with col3:
            make_model = st.text_input("Make & Model", placeholder="e.g., Volvo FH16")
            year = st.number_input("Year", min_value=1990, max_value=datetime.now().year, value=2020)
        
        with col4:
            engine_type = st.selectbox("Engine Type", ["Diesel", "Petrol", "Hybrid", "Electric"])
            status = st.selectbox("Status", ["Active", "Maintenance", "Out of Service"])
        
        submitted = st.form_submit_button("Add Vehicle", type="primary")
        
        if submitted:
            if not plate_number or not driver_name:
                st.error("Plate Number and Driver Name are required fields!")
            else:
                # Extract permit numbers from selected permits
                permit_numbers = []
                for selected in selected_permits:
                    permit_number = selected.split(" - ")[0]
                    permit_numbers.append(permit_number)
                
                vehicle_data = {
                    'plate_number': plate_number.upper(),
                    'driver_name': driver_name,
                    'helper_name': helper_name,
                    'route_permits': permit_numbers,  # Store as list of permit numbers
                    'tanker_size': tanker_size,
                    'vehicle_type': vehicle_type,
                    'make_model': make_model,
                    'year': year,
                    'engine_type': engine_type,
                    'status': status
                }
                
                success, message = data_manager.add_vehicle(vehicle_data)
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def show_vehicle_list(data_manager):
    """Display list of all vehicles"""
    st.subheader("Fleet Overview")
    
    vehicles = data_manager.get_vehicles()
    
    if not vehicles:
        st.info("No vehicles found. Add your first vehicle using the 'Add New Vehicle' tab.")
        return
    
    # Search and filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("Search by Plate Number or Driver", placeholder="Enter search term")
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Active", "Maintenance", "Out of Service"])
    
    with col3:
        vehicle_type_filter = st.selectbox("Filter by Type", ["All"] + list(set([v.get('vehicle_type', 'Unknown') for v in vehicles])))
    
    # Filter vehicles based on search and filters
    filtered_vehicles = vehicles
    
    if search_term:
        filtered_vehicles = [
            v for v in filtered_vehicles 
            if search_term.lower() in v.get('plate_number', '').lower() 
            or search_term.lower() in v.get('driver_name', '').lower()
        ]
    
    if status_filter != "All":
        filtered_vehicles = [v for v in filtered_vehicles if v.get('status') == status_filter]
    
    if vehicle_type_filter != "All":
        filtered_vehicles = [v for v in filtered_vehicles if v.get('vehicle_type') == vehicle_type_filter]
    
    # Display vehicles in cards
    st.write(f"Found {len(filtered_vehicles)} vehicle(s)")
    
    for vehicle in filtered_vehicles:
        with st.expander(f"🚛 {vehicle['plate_number']} - {vehicle['driver_name']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Vehicle Details:**")
                st.write(f"Plate Number: {vehicle['plate_number']}")
                st.write(f"Make & Model: {vehicle.get('make_model', 'N/A')}")
                st.write(f"Year: {vehicle.get('year', 'N/A')}")
                st.write(f"Type: {vehicle.get('vehicle_type', 'N/A')}")
                st.write(f"Engine: {vehicle.get('engine_type', 'N/A')}")
            
            with col2:
                st.write("**Personnel:**")
                st.write(f"Driver: {vehicle['driver_name']}")
                st.write(f"Helper: {vehicle.get('helper_name', 'N/A')}")
                st.write("**Specifications:**")
                st.write(f"Tanker Size: {vehicle.get('tanker_size', 0)} L")
                
                # Display route permits
                route_permits = vehicle.get('route_permits', [])
                if route_permits:
                    st.write("**Route Permits:**")
                    for permit in route_permits:
                        st.write(f"• {permit}")
                else:
                    st.write("Route Permits: None assigned")
            
            with col3:
                st.write("**Status & Info:**")
                status = vehicle.get('status', 'Unknown')
                status_color = {
                    'Active': '🟢',
                    'Maintenance': '🟡',
                    'Out of Service': '🔴'
                }.get(status, '⚫')
                st.write(f"Status: {status_color} {status}")
                
                if 'created_at' in vehicle:
                    created_date = datetime.fromisoformat(vehicle['created_at']).strftime("%Y-%m-%d")
                    st.write(f"Added: {created_date}")
            
            # Action buttons
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button(f"View Maintenance", key=f"maint_{vehicle['plate_number']}"):
                    st.session_state.selected_vehicle = vehicle['plate_number']
                    st.info(f"Switch to Maintenance Tracking tab to view records for {vehicle['plate_number']}")
            
            with col_btn2:
                if st.button(f"View Permits", key=f"permits_{vehicle['plate_number']}"):
                    st.session_state.selected_vehicle = vehicle['plate_number']
                    st.info(f"Switch to Route Permits & Tax tab to view permits for {vehicle['plate_number']}")
            
            with col_btn3:
                # Quick status update
                new_status = st.selectbox(
                    "Update Status", 
                    ["Active", "Maintenance", "Out of Service"],
                    index=["Active", "Maintenance", "Out of Service"].index(vehicle.get('status', 'Active')),
                    key=f"status_{vehicle['plate_number']}"
                )
                if new_status != vehicle.get('status'):
                    if st.button(f"Update", key=f"update_status_{vehicle['plate_number']}"):
                        data_manager.update_vehicle(vehicle['plate_number'], {'status': new_status})
                        st.success(f"Status updated to {new_status}")
                        st.rerun()
    
    # Summary statistics
    if filtered_vehicles:
        st.subheader("Fleet Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Vehicles", len(filtered_vehicles))
        
        with col2:
            active_count = len([v for v in filtered_vehicles if v.get('status') == 'Active'])
            st.metric("Active Vehicles", active_count)
        
        with col3:
            maintenance_count = len([v for v in filtered_vehicles if v.get('status') == 'Maintenance'])
            st.metric("In Maintenance", maintenance_count)
        
        with col4:
            total_capacity = sum([v.get('tanker_size', 0) for v in filtered_vehicles])
            st.metric("Total Capacity", f"{total_capacity:,} L")

def show_edit_vehicle_form(data_manager):
    """Form to edit existing vehicle"""
    st.subheader("Edit Vehicle")
    
    vehicles = data_manager.get_vehicles()
    
    if not vehicles:
        st.info("No vehicles available to edit. Add vehicles first.")
        return
    
    # Vehicle selection
    vehicle_options = [f"{v['plate_number']} - {v['driver_name']}" for v in vehicles]
    selected_vehicle_option = st.selectbox("Select Vehicle to Edit", vehicle_options)
    
    if not selected_vehicle_option:
        return
    
    selected_plate = selected_vehicle_option.split(" - ")[0]
    vehicle_data = data_manager.get_vehicle_by_plate(selected_plate)
    
    if not vehicle_data:
        st.error("Vehicle not found")
        return
    
    with st.form("edit_vehicle_form"):
        st.write(f"**Editing Vehicle: {vehicle_data['plate_number']}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            driver_name = st.text_input("Driver Name*", value=vehicle_data.get('driver_name', ''))
            helper_name = st.text_input("Helper Name", value=vehicle_data.get('helper_name', ''))
            tanker_size = st.number_input("Tanker Size (Liters)", min_value=0, value=vehicle_data.get('tanker_size', 0), step=100)
        
        with col2:
            vehicle_type = st.selectbox("Vehicle Type", 
                                      ["Tanker", "Container", "Flatbed", "Box Truck", "Other"],
                                      index=["Tanker", "Container", "Flatbed", "Box Truck", "Other"].index(vehicle_data.get('vehicle_type', 'Tanker')))
            engine_type = st.selectbox("Engine Type", 
                                     ["Diesel", "Petrol", "Hybrid", "Electric"],
                                     index=["Diesel", "Petrol", "Hybrid", "Electric"].index(vehicle_data.get('engine_type', 'Diesel')))
            status = st.selectbox("Status", 
                                ["Active", "Maintenance", "Out of Service"],
                                index=["Active", "Maintenance", "Out of Service"].index(vehicle_data.get('status', 'Active')))
        
        # Route permits selection
        st.subheader("Route Permits")
        permits = data_manager.get_permits()
        available_permits = [f"{p['permit_number']} - {p['location']}" for p in permits]
        
        # Get current permits for this vehicle
        current_permits = vehicle_data.get('route_permits', [])
        current_permit_options = []
        
        for permit_num in current_permits:
            # Find the full permit info
            for permit in permits:
                if permit['permit_number'] == permit_num:
                    current_permit_options.append(f"{permit['permit_number']} - {permit['location']}")
                    break
        
        if available_permits:
            selected_permits = st.multiselect(
                "Select Route Permits (multiple allowed)",
                available_permits,
                default=current_permit_options,
                help="You can select multiple permits for this vehicle"
            )
        else:
            st.info("No permits available. Add permits first in the Permits & Tax section.")
            selected_permits = []
        
        # Additional details
        st.subheader("Additional Information")
        col3, col4 = st.columns(2)
        
        with col3:
            make_model = st.text_input("Make & Model", value=vehicle_data.get('make_model', ''))
            year = st.number_input("Year", min_value=1990, max_value=datetime.now().year, value=vehicle_data.get('year', 2020))
        
        with col4:
            st.write("**Vehicle Information:**")
            st.write(f"Plate Number: {vehicle_data['plate_number']}")
            if 'created_at' in vehicle_data:
                created_date = datetime.fromisoformat(vehicle_data['created_at']).strftime("%Y-%m-%d %H:%M")
                st.write(f"Created: {created_date}")
        
        submitted = st.form_submit_button("Update Vehicle", type="primary")
        
        if submitted:
            if not driver_name:
                st.error("Driver name is required!")
            else:
                # Extract permit numbers from selected permits
                permit_numbers = []
                for selected in selected_permits:
                    permit_number = selected.split(" - ")[0]
                    permit_numbers.append(permit_number)
                
                updated_data = {
                    'driver_name': driver_name,
                    'helper_name': helper_name,
                    'route_permits': permit_numbers,
                    'tanker_size': tanker_size,
                    'vehicle_type': vehicle_type,
                    'make_model': make_model,
                    'year': year,
                    'engine_type': engine_type,
                    'status': status
                }
                
                success, message = data_manager.update_vehicle(selected_plate, updated_data)
                
                if success:
                    st.success(f"Vehicle {selected_plate} updated successfully!")
                    if permit_numbers:
                        st.info(f"Assigned permits: {', '.join(permit_numbers)}")
                    else:
                        st.info("No permits assigned to this vehicle.")
                    st.rerun()
                else:
                    st.error(f"Failed to update vehicle: {message}")
