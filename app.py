import streamlit as st
import sys
import os

# Import all modules
from data_manager import DataManager
from dashboard_module import show_dashboard
from vehicle_module import show_vehicle_management
from maintenance_module import show_maintenance_management
from inventory_module import show_inventory_management
from permit_module import show_permit_management
from load_module import show_load_management

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Truck Fleet Management System",
        page_icon="🚛",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize data manager
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    # Main title
    st.title("🚛 Truck Fleet Management System")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Create tabs for different modules
    tab_options = [
        "Dashboard",
        "Vehicle Management", 
        "Load Management",
        "Maintenance Tracking",
        "Inventory Management",
        "Route Permits & Tax"
    ]
    
    selected_tab = st.sidebar.selectbox("Select Module", tab_options)
    
    # Route to appropriate module based on selection
    if selected_tab == "Dashboard":
        show_dashboard(st.session_state.data_manager)
    elif selected_tab == "Vehicle Management":
        show_vehicle_management(st.session_state.data_manager)
    elif selected_tab == "Load Management":
        show_load_management(st.session_state.data_manager)
    elif selected_tab == "Maintenance Tracking":
        show_maintenance_management(st.session_state.data_manager)
    elif selected_tab == "Inventory Management":
        show_inventory_management(st.session_state.data_manager)
    elif selected_tab == "Route Permits & Tax":
        show_permit_management(st.session_state.data_manager)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Fleet Management System v1.0**")
    st.sidebar.markdown("Manage your truck fleet efficiently")

if __name__ == "__main__":
    main()
