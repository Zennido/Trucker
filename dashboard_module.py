import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_dashboard(data_manager):
    """Display main dashboard with overview and metrics"""
    st.header("📊 Fleet Management Dashboard")
    
    # Load all data
    vehicles = data_manager.get_vehicles()
    maintenance_records = data_manager.get_maintenance_records()
    inventory = data_manager.get_inventory()
    permits = data_manager.get_permits()
    tax_records = data_manager.get_token_tax()
    
    if not vehicles:
        st.warning("No vehicles found in the system. Please add vehicles to see dashboard analytics.")
        return
    
    # Key Performance Indicators
    show_kpi_metrics(vehicles, maintenance_records, inventory, permits, tax_records)
    
    # Alert Section
    show_alerts_section(data_manager)
    
    # Charts and Analytics
    col1, col2 = st.columns(2)
    
    with col1:
        show_fleet_status_chart(vehicles)
        show_maintenance_cost_trends(maintenance_records)
    
    with col2:
        show_inventory_status(inventory)
        show_document_compliance(vehicles, permits, tax_records)
    
    # Recent Activity
    show_recent_activity(maintenance_records, permits, tax_records)
    
    # Monthly Summary
    show_monthly_summary(maintenance_records)

def show_kpi_metrics(vehicles, maintenance_records, inventory, permits, tax_records):
    """Display key performance indicators"""
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_vehicles = len(vehicles)
        active_vehicles = len([v for v in vehicles if v.get('status') == 'Active'])
        st.metric(
            "Fleet Size", 
            total_vehicles,
            f"{active_vehicles} Active"
        )
    
    with col2:
        # Calculate total fleet capacity
        total_capacity = sum([v.get('tanker_size', 0) for v in vehicles])
        active_capacity = sum([v.get('tanker_size', 0) for v in vehicles if v.get('status') == 'Active'])
        st.metric(
            "Total Capacity",
            f"{total_capacity:,} L",
            f"{active_capacity:,} L Active"
        )
    
    with col3:
        # Maintenance costs (last 30 days)
        recent_date = datetime.now() - timedelta(days=30)
        recent_maintenance = [
            m for m in maintenance_records 
            if datetime.fromisoformat(m['maintenance_date']) >= recent_date
        ]
        monthly_cost = sum([m.get('total_cost', 0) for m in recent_maintenance])
        st.metric(
            "Monthly Maintenance",
            f"${monthly_cost:,.2f}",
            f"{len(recent_maintenance)} Records"
        )
    
    with col4:
        # Inventory value estimate
        inventory_items = inventory['oil'] + inventory['air_filter'] + inventory['tires']
        low_stock_count = sum([1 for item, qty in inventory.items() if qty < 5])
        st.metric(
            "Inventory Items",
            inventory_items,
            f"{low_stock_count} Low Stock" if low_stock_count > 0 else "Well Stocked"
        )
    
    with col5:
        # Document compliance
        current_date = datetime.now().date()
        valid_permits = len([p for p in permits if datetime.fromisoformat(p['expire_date']).date() > current_date])
        valid_taxes = len([t for t in tax_records if datetime.fromisoformat(t['expire_date']).date() > current_date])
        compliance_rate = ((valid_permits + valid_taxes) / max(len(permits) + len(tax_records), 1)) * 100
        st.metric(
            "Compliance Rate",
            f"{compliance_rate:.1f}%",
            f"{valid_permits + valid_taxes} Valid Docs"
        )

def show_alerts_section(data_manager):
    """Display critical alerts and warnings"""
    st.subheader("🚨 Alerts & Notifications")
    
    # Get all alerts
    maintenance_alerts = data_manager.get_maintenance_alerts()
    expiring_permits = data_manager.get_expiring_permits(30)
    expiring_taxes = data_manager.get_expiring_taxes(30)
    inventory = data_manager.get_inventory()
    
    # Count different types of alerts
    critical_alerts = []
    warning_alerts = []
    
    # Maintenance alerts
    for alert in maintenance_alerts:
        try:
            alert_type = alert['alert_type']
        except KeyError:
            alert_type = alert.get('alert', 'No details')

    if alert['priority'] == 'high':
        critical_alerts.append(f"🔧 {alert['plate_number']}: {alert_type}")
    else:
        warning_alerts.append(f"🔧 {alert['plate_number']}: {alert_type}")

    
    # Document expiration alerts
    current_date = datetime.now().date()
    for permit in expiring_permits:
        days = (datetime.fromisoformat(permit['expire_date']).date() - current_date).days
        if days <= 7:
            critical_alerts.append(f"📋 {permit['plate_number']}: Permit expires in {days} day(s)")
        else:
            warning_alerts.append(f"📋 {permit['plate_number']}: Permit expires in {days} day(s)")
    
    for tax in expiring_taxes:
        days = (datetime.fromisoformat(tax['expire_date']).date() - current_date).days
        if days <= 7:
            critical_alerts.append(f"💰 {tax['plate_number']}: Tax expires in {days} day(s)")
        else:
            warning_alerts.append(f"💰 {tax['plate_number']}: Tax expires in {days} day(s)")
    
    # Inventory alerts
    for item, quantity in inventory.items():
        if quantity == 0:
            critical_alerts.append(f"📦 {item.replace('_', ' ').title()}: Out of stock")
        elif quantity < 5:
            warning_alerts.append(f"📦 {item.replace('_', ' ').title()}: Low stock ({quantity} units)")
    
    # Display alerts
    if critical_alerts or warning_alerts:
        col1, col2 = st.columns(2)
        
        with col1:
            if critical_alerts:
                st.error(f"🚨 {len(critical_alerts)} Critical Alert(s)")
                for alert in critical_alerts[:5]:  # Show max 5 critical alerts
                    st.error(alert)
                if len(critical_alerts) > 5:
                    st.error(f"... and {len(critical_alerts) - 5} more critical alerts")
        
        with col2:
            if warning_alerts:
                st.warning(f"⚠️ {len(warning_alerts)} Warning(s)")
                for alert in warning_alerts[:5]:  # Show max 5 warnings
                    st.warning(alert)
                if len(warning_alerts) > 5:
                    st.warning(f"... and {len(warning_alerts) - 5} more warnings")
    else:
        st.success("✅ All systems operational - No critical alerts")

def show_fleet_status_chart(vehicles):
    """Display fleet status distribution chart"""
    st.subheader("🚛 Fleet Status Distribution")
    
    # Count vehicles by status
    status_counts = {}
    for vehicle in vehicles:
        status = vehicle.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        # Create pie chart
        fig = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="Vehicle Status Distribution",
            color_discrete_map={
                'Active': '#00cc96',
                'Maintenance': '#ffa15a', 
                'Out of Service': '#ef553b'
            }
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No vehicle status data available")

def show_maintenance_cost_trends(maintenance_records):
    """Display maintenance cost trends over time"""
    st.subheader("💰 Maintenance Cost Trends")
    
    if not maintenance_records:
        st.info("No maintenance records available")
        return
    
    # Prepare data for chart
    df = pd.DataFrame(maintenance_records)
    df['maintenance_date'] = pd.to_datetime(df['maintenance_date'])
    df['month'] = df['maintenance_date'].dt.to_period('M')
    
    # Group by month and sum costs
    monthly_costs = df.groupby('month')['total_cost'].sum().reset_index()
    monthly_costs['month'] = monthly_costs['month'].astype(str)
    
    if len(monthly_costs) > 0:
        # Create line chart
        fig = px.line(
            monthly_costs,
            x='month',
            y='total_cost',
            title='Monthly Maintenance Costs',
            markers=True
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Cost ($)",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show trend summary
        if len(monthly_costs) >= 2:
            latest_cost = monthly_costs.iloc[-1]['total_cost']
            previous_cost = monthly_costs.iloc[-2]['total_cost']
            change = latest_cost - previous_cost
            change_pct = (change / previous_cost * 100) if previous_cost > 0 else 0
            
            if change > 0:
                st.info(f"📈 Costs increased by ${change:.2f} ({change_pct:+.1f}%) from last month")
            elif change < 0:
                st.info(f"📉 Costs decreased by ${abs(change):.2f} ({change_pct:+.1f}%) from last month")
            else:
                st.info("➡️ Costs remained stable from last month")
    else:
        st.info("Insufficient data for trend analysis")

def show_inventory_status(inventory):
    """Display inventory status chart"""
    st.subheader("📦 Inventory Status")
    
    # Prepare inventory data
    items = []
    quantities = []
    status_colors = []
    
    item_names = {
        'oil': 'Engine Oil',
        'air_filter': 'Air Filters',
        'tires': 'Tires'
    }
    
    for item_key, quantity in inventory.items():
        items.append(item_names.get(item_key, item_key))
        quantities.append(quantity)
        
        # Determine status color
        if quantity == 0:
            status_colors.append('#ef553b')  # Red for out of stock
        elif quantity < 5:
            status_colors.append('#ffa15a')  # Orange for low stock
        elif quantity < 20:
            status_colors.append('#ffcc00')  # Yellow for moderate stock
        else:
            status_colors.append('#00cc96')  # Green for good stock
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=items,
            y=quantities,
            marker_color=status_colors,
            text=quantities,
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Current Inventory Levels",
        xaxis_title="Items",
        yaxis_title="Quantity",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Inventory status summary
    total_items = sum(quantities)
    low_stock_items = len([q for q in quantities if q < 5])
    
    if low_stock_items > 0:
        st.warning(f"⚠️ {low_stock_items} item(s) need restocking")
    else:
        st.success("✅ All inventory levels are adequate")

def show_document_compliance(vehicles, permits, tax_records):
    """Display document compliance status"""
    st.subheader("📋 Document Compliance")
    
    current_date = datetime.now().date()
    
    # Calculate compliance for each vehicle
    compliance_data = []
    
    for vehicle in vehicles:
        plate = vehicle['plate_number']
        
        # Check permits
        vehicle_permits = [p for p in permits if p['plate_number'] == plate]
        valid_permits = [p for p in vehicle_permits if datetime.fromisoformat(p['expire_date']).date() > current_date]
        
        # Check taxes
        vehicle_taxes = [t for t in tax_records if t['plate_number'] == plate]
        valid_taxes = [t for t in vehicle_taxes if datetime.fromisoformat(t['expire_date']).date() > current_date]
        
        # Determine compliance status
        has_permit = len(valid_permits) > 0
        has_tax = len(valid_taxes) > 0
        
        if has_permit and has_tax:
            status = "Compliant"
            color = "#00cc96"
        elif has_permit or has_tax:
            status = "Partial"
            color = "#ffa15a"
        else:
            status = "Non-Compliant"
            color = "#ef553b"
        
        compliance_data.append({
            'vehicle': plate,
            'status': status,
            'color': color,
            'permits': len(valid_permits),
            'taxes': len(valid_taxes)
        })
    
    # Count compliance status
    status_counts = {}
    for item in compliance_data:
        status = item['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Create compliance chart
    if status_counts:
        fig = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="Document Compliance Status",
            color_discrete_map={
                'Compliant': '#00cc96',
                'Partial': '#ffa15a',
                'Non-Compliant': '#ef553b'
            }
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Compliance summary
        total_vehicles = len(vehicles)
        compliant_vehicles = status_counts.get('Compliant', 0)
        compliance_rate = (compliant_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0
        
        st.metric(
            "Overall Compliance Rate",
            f"{compliance_rate:.1f}%",
            f"{compliant_vehicles}/{total_vehicles} vehicles"
        )
    else:
        st.info("No compliance data available")

def show_recent_activity(maintenance_records, permits, tax_records):
    """Display recent activity feed"""
    st.subheader("🕒 Recent Activity")
    
    # Combine all recent activities
    activities = []
    
    # Recent maintenance
    recent_maintenance = sorted(
        maintenance_records,
        key=lambda x: x['created_at'],
        reverse=True
    )[:5]
    
    for record in recent_maintenance:
        activities.append({
            'date': record['created_at'],
            'type': 'Maintenance',
            'description': f"Maintenance performed on {record['plate_number']} - {record.get('maintenance_type', 'Service')}",
            'cost': record.get('total_cost', 0)
        })
    
    # Recent permits
    recent_permits = sorted(
        permits,
        key=lambda x: x['created_at'],
        reverse=True
    )[:3]
    
    for permit in recent_permits:
        activities.append({
            'date': permit['created_at'],
            'type': 'Permit',
            'description': f"Route permit added for {permit['plate_number']} - {permit['location']}",
            'cost': permit.get('permit_fee', 0)
        })
    
    # Recent tax records
    recent_taxes = sorted(
        tax_records,
        key=lambda x: x['created_at'],
        reverse=True
    )[:3]
    
    for tax in recent_taxes:
        activities.append({
            'date': tax['created_at'],
            'type': 'Tax',
            'description': f"Tax payment for {tax['plate_number']} - {tax.get('tax_type', 'Token Tax')}",
            'cost': tax.get('total_paid', 0)
        })
    
    # Sort all activities by date
    activities.sort(key=lambda x: x['date'], reverse=True)
    
    # Display activities
    if activities:
        for activity in activities[:10]:  # Show last 10 activities
            activity_date = datetime.fromisoformat(activity['date']).strftime("%Y-%m-%d %H:%M")
            
            # Choose icon based on type
            icon = {
                'Maintenance': '🔧',
                'Permit': '📋',
                'Tax': '💰'
            }.get(activity['type'], '📝')
            
            with st.container():
                col1, col2, col3 = st.columns([1, 6, 2])
                
                with col1:
                    st.write(icon)
                
                with col2:
                    st.write(f"**{activity['description']}**")
                    st.caption(f"{activity_date} • {activity['type']}")
                
                with col3:
                    if activity['cost'] > 0:
                        st.write(f"${activity['cost']:.2f}")
                
                st.divider()
    else:
        st.info("No recent activity to display")

def show_monthly_summary(maintenance_records):
    """Display monthly summary statistics"""
    st.subheader("📊 Monthly Summary")
    
    current_month = datetime.now().replace(day=1)
    
    # Filter current month records
    current_month_records = [
        record for record in maintenance_records
        if datetime.fromisoformat(record['maintenance_date']).replace(day=1) == current_month
    ]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        monthly_maintenance_count = len(current_month_records)
        st.metric("This Month", f"{monthly_maintenance_count}", "Maintenance Records")
    
    with col2:
        monthly_cost = sum([record.get('total_cost', 0) for record in current_month_records])
        st.metric("Total Spent", f"${monthly_cost:,.2f}", "This Month")
    
    with col3:
        oil_changes = len([record for record in current_month_records if record.get('oil_changed')])
        st.metric("Oil Changes", oil_changes, "This Month")
    
    with col4:
        avg_cost = monthly_cost / monthly_maintenance_count if monthly_maintenance_count > 0 else 0
        st.metric("Avg Cost", f"${avg_cost:.2f}", "Per Service")
    
    # Performance indicators
    if maintenance_records:
        # Compare with previous month
        previous_month = (current_month - timedelta(days=1)).replace(day=1)
        previous_month_records = [
            record for record in maintenance_records
            if datetime.fromisoformat(record['maintenance_date']).replace(day=1) == previous_month
        ]
        
        prev_count = len(previous_month_records)
        prev_cost = sum([record.get('total_cost', 0) for record in previous_month_records])
        
        st.write("**Month-over-Month Comparison:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            count_change = monthly_maintenance_count - prev_count
            count_pct = (count_change / prev_count * 100) if prev_count > 0 else 0
            st.write(f"Maintenance Records: {count_change:+d} ({count_pct:+.1f}%)")
        
        with col2:
            cost_change = monthly_cost - prev_cost
            cost_pct = (cost_change / prev_cost * 100) if prev_cost > 0 else 0
            st.write(f"Total Cost: ${cost_change:+,.2f} ({cost_pct:+.1f}%)")
