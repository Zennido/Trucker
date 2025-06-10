import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def show_permit_management(data_manager):
    """Display permit and tax management interface"""
    st.header("📋 Route Permits & Token Tax")
    
    # Create tabs for different permit operations
    tab1, tab2, tab3, tab4 = st.tabs(["Route Permits", "Token Tax", "Expiration Alerts", "Documents"])
    
    with tab1:
        show_route_permits(data_manager)
    
    with tab2:
        show_token_tax(data_manager)
    
    with tab3:
        show_expiration_alerts(data_manager)
    
    with tab4:
        show_documents_overview(data_manager)

def show_route_permits(data_manager):
    """Manage route permits"""
    st.subheader("Route Permits Management")
    
    # Add new permit form
    with st.expander("Add New Route Permit", expanded=False):
        with st.form("add_permit_form"):
            # Vehicle selection
            vehicles = data_manager.get_vehicles()
            if not vehicles:
                st.warning("No vehicles found. Please add vehicles first.")
                st.form_submit_button("Add Permit", disabled=True)
                return
            
            vehicle_options = [f"{v['plate_number']} - {v['driver_name']}" for v in vehicles]
            selected_vehicle = st.selectbox("Select Vehicle*", vehicle_options)
            plate_number = selected_vehicle.split(" - ")[0] if selected_vehicle else ""
            
            permit_number = st.text_input("Permit Number*", placeholder="Enter permit number")
            location = st.text_input("Location/Route*", placeholder="e.g., City A to City B, Highway 101")
            expire_date = st.date_input("Expiry Date*", value=datetime.now().date() + timedelta(days=365))
            
            submitted = st.form_submit_button("Add Permit", type="primary")
            
            if submitted:
                if not all([permit_number, location]):
                    st.error("Please fill in all required fields (marked with *)!")
                else:
                    permit_data = {
                        'plate_number': plate_number,
                        'permit_number': permit_number,
                        'location': location,
                        'expire_date': expire_date.isoformat(),
                        'status': 'Active'
                    }
                    
                    success, message = data_manager.add_permit(permit_data)
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    # Display existing permits
    st.subheader("Current Route Permits")
    
    permits = data_manager.get_permits()
    
    if not permits:
        st.info("No route permits found. Add your first permit using the form above.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vehicle_filter = st.selectbox("Filter by Vehicle", ["All Vehicles"] + [p['plate_number'] for p in permits])
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Active", "Expired", "Expiring Soon"])
    
    with col3:
        location_filter = st.selectbox("Filter by Location", ["All Locations"] + list(set([p['location'] for p in permits])))
    
    # Apply filters
    filtered_permits = permits
    
    if vehicle_filter != "All Vehicles":
        filtered_permits = [p for p in filtered_permits if p['plate_number'] == vehicle_filter]
    
    if location_filter != "All Locations":
        filtered_permits = [p for p in filtered_permits if p['location'] == location_filter]
    
    # Status filter logic
    current_date = datetime.now().date()
    if status_filter == "Active":
        filtered_permits = [p for p in filtered_permits if datetime.fromisoformat(p['expire_date']).date() > current_date]
    elif status_filter == "Expired":
        filtered_permits = [p for p in filtered_permits if datetime.fromisoformat(p['expire_date']).date() <= current_date]
    elif status_filter == "Expiring Soon":
        soon_date = current_date + timedelta(days=30)
        filtered_permits = [p for p in filtered_permits if current_date < datetime.fromisoformat(p['expire_date']).date() <= soon_date]
    
    # Sort by expiry date
    filtered_permits.sort(key=lambda x: x['expire_date'])
    
    st.write(f"Found {len(filtered_permits)} permit(s)")
    
    # Display permits
    for permit in filtered_permits:
        expire_date = datetime.fromisoformat(permit['expire_date']).date()
        days_to_expire = (expire_date - current_date).days
        
        # Determine status color
        if days_to_expire < 0:
            status_emoji = "🔴"
            status_text = "EXPIRED"
        elif days_to_expire <= 7:
            status_emoji = "🟠"
            status_text = "CRITICAL"
        elif days_to_expire <= 30:
            status_emoji = "🟡"
            status_text = "WARNING"
        else:
            status_emoji = "🟢"
            status_text = "ACTIVE"
        
        with st.expander(
            f"{status_emoji} {permit['permit_number']} - {permit['plate_number']} ({permit['location']}) - {status_text}",
            expanded=False
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Permit Information:**")
                st.write(f"Number: {permit['permit_number']}")
                st.write(f"Vehicle: {permit['plate_number']}")
                st.write(f"Location/Route: {permit['location']}")
            
            with col2:
                st.write("**Validity:**")
                st.write(f"Expires: {permit['expire_date']}")
                st.write(f"Days Remaining: {days_to_expire}")
                st.write(f"Status: {status_emoji} {status_text}")
            
            with col3:
                if days_to_expire <= 30:
                    st.write("**Action Required:**")
                    if days_to_expire <= 0:
                        st.error("EXPIRED - Renewal required")
                    elif days_to_expire <= 7:
                        st.error("CRITICAL - Expires very soon")
                    else:
                        st.warning("WARNING - Expires within 30 days")
            
            # Action buttons
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if days_to_expire <= 30:
                    if st.button(f"Mark for Renewal", key=f"renew_{permit['permit_number']}"):
                        st.info("Renewal process initiated. Please follow up with issuing authority.")
            
            with col_btn2:
                if st.button(f"Update Status", key=f"update_{permit['permit_number']}"):
                    st.info("Status update feature - implement based on your workflow needs.")

def show_token_tax(data_manager):
    """Manage token tax records"""
    st.subheader("Token Tax Management")
    
    # Add new token tax record
    with st.expander("Add Token Tax Record", expanded=False):
        with st.form("add_token_tax_form"):
            # Vehicle selection
            vehicles = data_manager.get_vehicles()
            if not vehicles:
                st.warning("No vehicles found. Please add vehicles first.")
                st.form_submit_button("Add Tax Record", disabled=True)
                return
            
            vehicle_options = [f"{v['plate_number']} - {v['driver_name']}" for v in vehicles]
            selected_vehicle = st.selectbox("Select Vehicle*", vehicle_options)
            plate_number = selected_vehicle.split(" - ")[0] if selected_vehicle else ""
            
            expire_date = st.date_input("Expiry Date*", value=datetime.now().date() + timedelta(days=365))
            
            submitted = st.form_submit_button("Add Tax Record", type="primary")
            
            if submitted:
                if not expire_date:
                    st.error("Please fill in the expiry date!")
                else:
                    tax_data = {
                        'plate_number': plate_number,
                        'expire_date': expire_date.isoformat(),
                        'status': 'Active'
                    }
                    
                    success, message = data_manager.add_token_tax(tax_data)
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    # Display existing tax records
    st.subheader("Token Tax Records")
    
    tax_records = data_manager.get_token_tax()
    
    if not tax_records:
        st.info("No token tax records found. Add your first record using the form above.")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        vehicle_filter = st.selectbox("Filter by Vehicle", ["All Vehicles"] + [t['plate_number'] for t in tax_records], key="tax_vehicle_filter")
    
    with col2:
        tax_type_filter = st.selectbox("Filter by Tax Type", ["All Types"] + list(set([t.get('tax_type', 'Unknown') for t in tax_records])))
    
    # Apply filters
    filtered_tax_records = tax_records
    
    if vehicle_filter != "All Vehicles":
        filtered_tax_records = [t for t in filtered_tax_records if t['plate_number'] == vehicle_filter]
    
    if tax_type_filter != "All Types":
        filtered_tax_records = [t for t in filtered_tax_records if t.get('tax_type') == tax_type_filter]
    
    # Sort by expiry date
    filtered_tax_records.sort(key=lambda x: x['expire_date'])
    
    st.write(f"Found {len(filtered_tax_records)} tax record(s)")
    
    # Display tax records
    current_date = datetime.now().date()
    
    for tax_record in filtered_tax_records:
        expire_date = datetime.fromisoformat(tax_record['expire_date']).date()
        days_to_expire = (expire_date - current_date).days
        
        # Determine status
        if days_to_expire < 0:
            status_emoji = "🔴"
            status_text = "EXPIRED"
        elif days_to_expire <= 7:
            status_emoji = "🟠"
            status_text = "CRITICAL"
        elif days_to_expire <= 30:
            status_emoji = "🟡"
            status_text = "DUE SOON"
        else:
            status_emoji = "🟢"
            status_text = "CURRENT"
        
        with st.expander(
            f"{status_emoji} {tax_record['plate_number']} - {tax_record.get('tax_type', 'Token Tax')} - {status_text}",
            expanded=False
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Tax Information:**")
                st.write(f"Type: {tax_record.get('tax_type', 'N/A')}")
                st.write(f"Vehicle: {tax_record['plate_number']}")
                st.write(f"Amount: ${tax_record.get('tax_amount', 0):.2f}")
                st.write(f"Late Fee: ${tax_record.get('late_fee', 0):.2f}")
                st.write(f"Penalty: ${tax_record.get('penalty_amount', 0):.2f}")
                st.write(f"**Total Paid: ${tax_record.get('total_paid', 0):.2f}**")
            
            with col2:
                st.write("**Payment Details:**")
                st.write(f"Payment Date: {tax_record['payment_date']}")
                st.write(f"Paid To: {tax_record.get('paid_to', 'N/A')}")
                st.write(f"Method: {tax_record.get('payment_method', 'N/A')}")
                st.write(f"Receipt: {tax_record.get('receipt_number', 'N/A')}")
                if tax_record.get('vehicle_value', 0) > 0:
                    st.write(f"Vehicle Value: ${tax_record['vehicle_value']:,.2f}")
            
            with col3:
                st.write("**Validity:**")
                st.write(f"Expires: {tax_record['expire_date']}")
                st.write(f"Days Remaining: {days_to_expire}")
                st.write(f"Status: {status_emoji} {status_text}")
                
                if tax_record.get('previous_expire'):
                    st.write(f"Previous Expiry: {tax_record['previous_expire']}")
            
            if tax_record.get('notes'):
                st.write("**Notes:**")
                st.write(tax_record['notes'])

def show_expiration_alerts(data_manager):
    """Show expiration alerts for permits and taxes"""
    st.subheader("Expiration Alerts")
    
    # Get expiring permits and taxes
    expiring_permits = data_manager.get_expiring_permits(30)  # 30 days ahead
    expiring_taxes = data_manager.get_expiring_taxes(30)
    
    if not expiring_permits and not expiring_taxes:
        st.success("✅ No permits or taxes expiring in the next 30 days!")
        return
    
    # Critical alerts (7 days or less)
    critical_permits = [p for p in expiring_permits if (datetime.fromisoformat(p['expire_date']).date() - datetime.now().date()).days <= 7]
    critical_taxes = [t for t in expiring_taxes if (datetime.fromisoformat(t['expire_date']).date() - datetime.now().date()).days <= 7]
    
    if critical_permits or critical_taxes:
        st.error(f"🚨 CRITICAL: {len(critical_permits + critical_taxes)} document(s) expiring within 7 days!")
        
        for permit in critical_permits:
            days = (datetime.fromisoformat(permit['expire_date']).date() - datetime.now().date()).days
            st.error(f"🔴 PERMIT: {permit['plate_number']} - {permit['permit_number']} expires in {days} day(s)")
        
        for tax in critical_taxes:
            days = (datetime.fromisoformat(tax['expire_date']).date() - datetime.now().date()).days
            st.error(f"🔴 TAX: {tax['plate_number']} - {tax.get('tax_type', 'Token Tax')} expires in {days} day(s)")
    
    # Warning alerts (8-30 days)
    warning_permits = [p for p in expiring_permits if (datetime.fromisoformat(p['expire_date']).date() - datetime.now().date()).days > 7]
    warning_taxes = [t for t in expiring_taxes if (datetime.fromisoformat(t['expire_date']).date() - datetime.now().date()).days > 7]
    
    if warning_permits or warning_taxes:
        st.warning(f"⚠️ WARNING: {len(warning_permits + warning_taxes)} document(s) expiring within 30 days")
        
        for permit in warning_permits:
            days = (datetime.fromisoformat(permit['expire_date']).date() - datetime.now().date()).days
            st.warning(f"🟡 PERMIT: {permit['plate_number']} - {permit['permit_number']} expires in {days} day(s)")
        
        for tax in warning_taxes:
            days = (datetime.fromisoformat(tax['expire_date']).date() - datetime.now().date()).days
            st.warning(f"🟡 TAX: {tax['plate_number']} - {tax.get('tax_type', 'Token Tax')} expires in {days} day(s)")
    
    # Renewal action center
    st.subheader("🔄 Renewal Action Center")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Quick Actions:**")
        if st.button("📧 Generate Renewal Reminders"):
            st.info("Renewal reminders generated for all expiring documents")
        
        if st.button("📋 Create Renewal Checklist"):
            renewal_items = []
            for permit in expiring_permits:
                renewal_items.append(f"Renew permit {permit['permit_number']} for {permit['plate_number']}")
            for tax in expiring_taxes:
                renewal_items.append(f"Renew {tax.get('tax_type', 'tax')} for {tax['plate_number']}")
            
            if renewal_items:
                st.write("**Renewal Checklist:**")
                for i, item in enumerate(renewal_items, 1):
                    st.write(f"{i}. ☐ {item}")
    
    with col2:
        st.write("**Renewal Calendar:**")
        
        # Create a simple calendar view of upcoming renewals
        renewal_calendar = {}
        
        for permit in expiring_permits:
            date = permit['expire_date']
            if date not in renewal_calendar:
                renewal_calendar[date] = []
            renewal_calendar[date].append(f"Permit: {permit['plate_number']}")
        
        for tax in expiring_taxes:
            date = tax['expire_date']
            if date not in renewal_calendar:
                renewal_calendar[date] = []
            renewal_calendar[date].append(f"Tax: {tax['plate_number']}")
        
        # Sort by date and display
        sorted_dates = sorted(renewal_calendar.keys())
        for date in sorted_dates[:10]:  # Show next 10 dates
            st.write(f"**{date}:**")
            for item in renewal_calendar[date]:
                st.write(f"  • {item}")

def show_documents_overview(data_manager):
    """Show overview of all documents and their status"""
    st.subheader("Documents Overview")
    
    vehicles = data_manager.get_vehicles()
    permits = data_manager.get_permits()
    tax_records = data_manager.get_token_tax()
    
    if not vehicles:
        st.info("No vehicles found. Add vehicles to start managing documents.")
        return
    
    # Create document status for each vehicle
    vehicle_documents = []
    
    for vehicle in vehicles:
        plate = vehicle['plate_number']
        
        # Get permits for this vehicle
        vehicle_permits = [p for p in permits if p['plate_number'] == plate]
        active_permits = [p for p in vehicle_permits if datetime.fromisoformat(p['expire_date']).date() > datetime.now().date()]
        
        # Get tax records for this vehicle
        vehicle_taxes = [t for t in tax_records if t['plate_number'] == plate]
        current_taxes = [t for t in vehicle_taxes if datetime.fromisoformat(t['expire_date']).date() > datetime.now().date()]
        
        # Determine document status
        permit_status = "✅" if active_permits else "❌"
        tax_status = "✅" if current_taxes else "❌"
        
        # Check for expiring documents
        expiring_permits = [p for p in active_permits if (datetime.fromisoformat(p['expire_date']).date() - datetime.now().date()).days <= 30]
        expiring_taxes = [t for t in current_taxes if (datetime.fromisoformat(t['expire_date']).date() - datetime.now().date()).days <= 30]
        
        if expiring_permits:
            permit_status = "⚠️"
        if expiring_taxes:
            tax_status = "⚠️"
        
        vehicle_documents.append({
            'Vehicle': f"{plate} - {vehicle['driver_name']}",
            'Route Permits': f"{permit_status} {len(active_permits)}",
            'Token Tax': f"{tax_status} {len(current_taxes)}",
            'Total Documents': len(vehicle_permits) + len(vehicle_taxes),
            'Status': "Complete" if active_permits and current_taxes else "Incomplete"
        })
    
    # Display as a table
    df_documents = pd.DataFrame(vehicle_documents)
    st.dataframe(df_documents, hide_index=True, use_container_width=True)
    
    # Document statistics
    st.subheader("Document Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_permits = len(permits)
        active_permits = len([p for p in permits if datetime.fromisoformat(p['expire_date']).date() > datetime.now().date()])
        st.metric("Route Permits", f"{active_permits}/{total_permits}", "Active/Total")
    
    with col2:
        total_taxes = len(tax_records)
        current_taxes = len([t for t in tax_records if datetime.fromisoformat(t['expire_date']).date() > datetime.now().date()])
        st.metric("Token Taxes", f"{current_taxes}/{total_taxes}", "Current/Total")
    
    with col3:
        complete_vehicles = len([v for v in vehicle_documents if v['Status'] == 'Complete'])
        st.metric("Compliant Vehicles", f"{complete_vehicles}/{len(vehicles)}", "Complete/Total")
    
    with col4:
        expiring_count = len(data_manager.get_expiring_permits(30)) + len(data_manager.get_expiring_taxes(30))
        st.metric("Expiring Soon", expiring_count, "Next 30 days")
    
    # Export functionality
    st.subheader("Export Documents")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export Permits Report"):
            df_permits = pd.DataFrame(permits) if permits else pd.DataFrame()
            if not df_permits.empty:
                csv = df_permits.to_csv(index=False)
                st.download_button(
                    label="Download Permits CSV",
                    data=csv,
                    file_name=f"permits_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    with col2:
        if st.button("📄 Export Tax Records"):
            df_taxes = pd.DataFrame(tax_records) if tax_records else pd.DataFrame()
            if not df_taxes.empty:
                csv = df_taxes.to_csv(index=False)
                st.download_button(
                    label="Download Tax Records CSV",
                    data=csv,
                    file_name=f"tax_records_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    with col3:
        if st.button("📊 Export Summary Report"):
            df_summary = pd.DataFrame(vehicle_documents)
            csv = df_summary.to_csv(index=False)
            st.download_button(
                label="Download Summary CSV",
                data=csv,
                file_name=f"documents_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
