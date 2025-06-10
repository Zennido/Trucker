import streamlit as st
import pandas as pd
from datetime import datetime, date
import json

def show_load_management(data_manager):
    """Display load management interface"""
    st.header("📦 Load Management")
    
    # Create tabs for different load operations
    tab1, tab2, tab3 = st.tabs(["Add New Load", "Load History", "Load Analytics"])
    
    with tab1:
        show_add_load_form(data_manager)
    
    with tab2:
        show_load_history(data_manager)
    
    with tab3:
        show_load_analytics(data_manager)

def show_add_load_form(data_manager):
    """Form to add a new load record"""
    st.subheader("Add New Load")
    
    vehicles = data_manager.get_vehicles()
    if not vehicles:
        st.warning("No vehicles found. Please add vehicles first.")
        return
    
    with st.form("add_load_form"):
        # Auto-generate load number
        existing_loads = data_manager.load_data('loads') if hasattr(data_manager, 'load_data') else []
        load_number = f"LD{len(existing_loads) + 1:06d}"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Load Number", value=load_number, disabled=True, help="Auto-generated load number")
            
            # Vehicle selection dropdown
            vehicle_options = [f"{v['plate_number']} - {v['driver_name']}" for v in vehicles]
            selected_vehicle = st.selectbox("Select Vehicle*", vehicle_options)
            plate_number = selected_vehicle.split(" - ")[0] if selected_vehicle else ""
            
            loading_date = st.date_input("Loading Date*", value=datetime.now().date())
            source = st.text_input("Source*", placeholder="e.g., Refinery A, Depot B")
        
        with col2:
            party_name = st.text_input("Party Name*", placeholder="Customer/Client name")
            contractor = st.text_input("Contractor", placeholder="Contractor name (if applicable)")
            destination = st.text_input("Destination", placeholder="Delivery location")
            
        # Weight and financial details
        st.subheader("Weight & Financial Details")
        col3, col4 = st.columns(2)
        
        with col3:
            gross_weight = st.number_input("Gross Weight (KG)*", min_value=0.0, step=100.0, help="Total weight including vehicle")
            tare_weight = st.number_input("Tare Weight (KG)*", min_value=0.0, step=100.0, help="Empty vehicle weight")
            net_weight = gross_weight - tare_weight if gross_weight > tare_weight else 0.0
            st.write(f"**Net Weight: {net_weight:,.2f} KG**")
        
        with col4:
            rate_per_unit = st.number_input("Rate per KG*", min_value=0.0, step=0.01, format="%.2f")
            amount = net_weight * rate_per_unit
            st.write(f"**Total Amount: PKR{amount:,.2f}**")
            
            advance_payment = st.number_input("Advance Payment", min_value=0.0, step=100.0)
            pending_amount = amount - advance_payment
            st.write(f"**Pending Amount: PKR{pending_amount:,.2f}**")
        
        # Additional details
        st.subheader("Additional Information")
        col5, col6 = st.columns(2)
        
        with col5:
            product_type = st.selectbox("Product Type", [
                "LPG"
            ])
            loading_time = st.time_input("Loading Time", value=datetime.now().time())
            
        with col6:
            delivery_date = st.date_input("Expected Delivery Date", value=datetime.now().date())
            delivery_time = st.time_input("Expected Delivery Time", value=datetime.now().time())
        
        # Status and notes
        status = st.selectbox("Load Status", ["Loading", "In Transit", "Delivered", "Cancelled"])
        notes = st.text_area("Notes", placeholder="Additional notes about this load")
        
        submitted = st.form_submit_button("Add Load Record", type="primary")
        
        if submitted:
            if not all([selected_vehicle, loading_date, source, party_name, gross_weight, tare_weight, rate_per_unit]):
                st.error("Please fill in all required fields (marked with *)!")
            elif net_weight <= 0:
                st.error("Net weight must be positive. Check gross and tare weights.")
            else:
                load_data = {
                    'load_number': load_number,
                    'plate_number': plate_number,
                    'loading_date': loading_date.isoformat(),
                    'source': source,
                    'destination': destination,
                    'gross_weight': gross_weight,
                    'tare_weight': tare_weight,
                    'net_weight': net_weight,
                    'rate_per_unit': rate_per_unit,
                    'amount': amount,
                    'advance_payment': advance_payment,
                    'pending_amount': pending_amount,
                    'party_name': party_name,
                    'contractor': contractor,
                    'product_type': product_type,
                    'loading_time': loading_time.isoformat(),
                    'delivery_date': delivery_date.isoformat(),
                    'delivery_time': delivery_time.isoformat(),
                    'status': status,
                    'notes': notes,
                    'created_at': datetime.now().isoformat()
                }
                
                success, message = data_manager.add_load(load_data)
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def show_load_history(data_manager):
    """Display load history with filters and search"""
    st.subheader("Load History")
    
    loads = data_manager.get_loads()
    
    if not loads:
        st.info("No load records found. Add your first load using the 'Add New Load' tab.")
        return
    
    # Filter options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        vehicle_filter = st.selectbox("Filter by Vehicle", ["All Vehicles"] + list(set([l['plate_number'] for l in loads])))
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All Status"] + list(set([l.get('status', 'Unknown') for l in loads])))
    
    with col3:
        party_filter = st.selectbox("Filter by Party", ["All Parties"] + list(set([l['party_name'] for l in loads])))
    
    with col4:
        date_range = st.selectbox("Date Range", ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"])
    
    # Search functionality
    search_term = st.text_input("Search by Load Number, Source, or Destination", placeholder="Enter search term")
    
    # Apply filters
    filtered_loads = loads
    
    if vehicle_filter != "All Vehicles":
        filtered_loads = [l for l in filtered_loads if l['plate_number'] == vehicle_filter]
    
    if status_filter != "All Status":
        filtered_loads = [l for l in filtered_loads if l.get('status') == status_filter]
    
    if party_filter != "All Parties":
        filtered_loads = [l for l in filtered_loads if l['party_name'] == party_filter]
    
    if search_term:
        search_term_lower = search_term.lower()
        filtered_loads = [
            l for l in filtered_loads 
            if search_term_lower in l['load_number'].lower() 
            or search_term_lower in l['source'].lower()
            or search_term_lower in l.get('destination', '').lower()
        ]
    
    if date_range != "All Time":
        from datetime import timedelta
        days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
        cutoff_date = datetime.now().date() - timedelta(days=days_map[date_range])
        filtered_loads = [
            l for l in filtered_loads 
            if datetime.fromisoformat(l['loading_date']).date() >= cutoff_date
        ]
    
    # Sort by loading date (newest first)
    filtered_loads.sort(key=lambda x: x['loading_date'], reverse=True)
    
    st.write(f"Found {len(filtered_loads)} load record(s)")
    
    # Display loads in expandable cards
    for load in filtered_loads:
        status_color = {
            'Loading': '🟡',
            'In Transit': '🔵', 
            'Delivered': '🟢',
            'Cancelled': '🔴'
        }.get(load.get('status', 'Unknown'), '⚫')
        
        with st.expander(
            f"{status_color} {load['load_number']} - {load['plate_number']} - {load['party_name']} ({load.get('status', 'Unknown')})",
            expanded=False
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Load Details:**")
                st.write(f"Load Number: {load['load_number']}")
                st.write(f"Vehicle: {load['plate_number']}")
                st.write(f"Loading Date: {load['loading_date']}")
                st.write(f"Source: {load['source']}")
                st.write(f"Destination: {load.get('destination', 'N/A')}")
                st.write(f"Product: {load.get('product_type', 'N/A')}")
            
            with col2:
                st.write("**Weight & Measurements:**")
                st.write(f"Gross Weight: {load['gross_weight']:,} KG")
                st.write(f"Tare Weight: {load['tare_weight']:,} KG")
                st.write(f"Net Weight: {load['net_weight']:,} KG")
                st.write(f"Rate: PKR{load['rate_per_unit']:.2f}/KG")
                
                st.write("**Parties:**")
                st.write(f"Party: {load['party_name']}")
                st.write(f"Contractor: {load.get('contractor', 'N/A')}")
            
            with col3:
                st.write("**Financial Details:**")
                st.write(f"Total Amount: PKR{load['amount']:,.2f}")
                st.write(f"Advance: PKR{load.get('advance_payment', 0):,.2f}")
                st.write(f"Pending: PKR{load.get('pending_amount', 0):,.2f}")
                
                st.write("**Status & Timing:**")
                st.write(f"Status: {status_color} {load.get('status', 'Unknown')}")
                st.write(f"Loading Time: {load.get('loading_time', 'N/A')}")
                st.write(f"Expected Delivery: {load.get('delivery_date', 'N/A')}")
            
            if load.get('notes'):
                st.write("**Notes:**")
                st.write(load['notes'])
            
            # Quick status update
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                new_status = st.selectbox(
                    "Update Status",
                    ["Loading", "In Transit", "Delivered", "Cancelled"],
                    index=["Loading", "In Transit", "Delivered", "Cancelled"].index(load.get('status', 'Loading')),
                    key=f"status_{load['load_number']}"
                )
            
            with col_btn2:
                if new_status != load.get('status'):
                    if st.button(f"Update Status", key=f"update_{load['load_number']}"):
                        data_manager.update_load_status(load['load_number'], new_status)
                        st.success(f"Status updated to {new_status}")
                        st.rerun()

def show_load_analytics(data_manager):
    """Display load analytics and statistics"""
    st.subheader("Load Analytics")
    
    loads = data_manager.get_loads()
    
    if not loads:
        st.info("No load data available for analytics.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_loads = len(loads)
        completed_loads = len([l for l in loads if l.get('status') == 'Delivered'])
        st.metric("Total Loads", total_loads, f"{completed_loads} Completed")
    
    with col2:
        total_weight = sum([l.get('net_weight', 0) for l in loads])
        st.metric("Total Weight", f"{total_weight:,.0f} KG")
    
    with col3:
        total_revenue = sum([l.get('amount', 0) for l in loads])
        st.metric("Total Revenue", f"PKR{total_revenue:,.2f}")
    
    with col4:
        pending_amount = sum([l.get('pending_amount', 0) for l in loads])
        st.metric("Pending Payments", f"PKR{pending_amount:,.2f}")
    
    # Charts and analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Load status distribution
        status_counts = {}
        for load in loads:
            status = load.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            import plotly.express as px
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Load Status Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top parties by load count
        party_counts = {}
        for load in loads:
            party = load['party_name']
            party_counts[party] = party_counts.get(party, 0) + 1
        
        if party_counts:
            top_parties = sorted(party_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            party_names = [p[0] for p in top_parties]
            party_loads = [p[1] for p in top_parties]
            
            import plotly.graph_objects as go
            fig = go.Figure(data=[go.Bar(x=party_names, y=party_loads)])
            fig.update_layout(title="Top 5 Parties by Load Count", xaxis_title="Party", yaxis_title="Number of Loads")
            st.plotly_chart(fig, use_container_width=True)
    
    # Monthly revenue trend
    if len(loads) > 0:
        df = pd.DataFrame(loads)
        df['loading_date'] = pd.to_datetime(df['loading_date'])
        df['month'] = df['loading_date'].dt.to_period('M')
        
        monthly_revenue = df.groupby('month')['amount'].sum().reset_index()
        monthly_revenue['month'] = monthly_revenue['month'].astype(str)
        
        if len(monthly_revenue) > 0:
            import plotly.express as px
            fig = px.line(
                monthly_revenue,
                x='month',
                y='amount',
                title='Monthly Revenue Trend',
                markers=True
            )
            fig.update_layout(xaxis_title="Month", yaxis_title="Revenue (PKR)")
            st.plotly_chart(fig, use_container_width=True)
    
    # Export functionality
    st.subheader("Export Load Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export All Loads to CSV"):
            df_export = pd.DataFrame(loads)
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"load_records_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("💰 Export Financial Summary"):
            financial_summary = []
            for load in loads:
                financial_summary.append({
                    'Load Number': load['load_number'],
                    'Party': load['party_name'],
                    'Amount': load.get('amount', 0),
                    'Advance': load.get('advance_payment', 0),
                    'Pending': load.get('pending_amount', 0),
                    'Status': load.get('status', 'Unknown')
                })
            
            df_financial = pd.DataFrame(financial_summary)
            csv = df_financial.to_csv(index=False)
            st.download_button(
                label="Download Financial CSV",
                data=csv,
                file_name=f"financial_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )