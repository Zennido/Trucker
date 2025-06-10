import json
import os
from datetime import datetime, timedelta
import pandas as pd

class DataManager:
    """Handles all data operations for the fleet management system"""
    
    def __init__(self):
        self.data_files = {
            'vehicles': 'vehicles.json',
            'maintenance': 'maintenance.json',
            'inventory': 'inventory.json',
            'permits': 'permits.json',
            'token_tax': 'token_tax.json',
            'loads': 'loads.json'
        }
        self.initialize_data_files()
    
    def initialize_data_files(self):
        """Initialize JSON data files if they don't exist"""
        default_data = {
            'vehicles': [],
            'maintenance': [],
            'inventory': {
                'oil': 0,
                'air_filter': 0,
                'tires': 0
            },
            'permits': [],
            'token_tax': [],
            'loads': []
        }
        
        for key, filename in self.data_files.items():
            if not os.path.exists(filename):
                self.save_data(key, default_data[key])
    
    def load_data(self, data_type):
        """Load data from JSON file"""
        try:
            filename = self.data_files[data_type]
            with open(filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            if data_type == 'inventory':
                return {'oil': 0, 'air_filter': 0, 'tires': 0}
            return []
    
    def save_data(self, data_type, data):
        """Save data to JSON file"""
        filename = self.data_files[data_type]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_vehicle(self, vehicle_data):
        """Add a new vehicle to the fleet"""
        vehicles = self.load_data('vehicles')
        
        # Check if plate number already exists
        for vehicle in vehicles:
            if vehicle['plate_number'] == vehicle_data['plate_number']:
                return False, "Vehicle with this plate number already exists"
        
        # Add timestamp
        vehicle_data['created_at'] = datetime.now().isoformat()
        vehicle_data['id'] = len(vehicles) + 1
        
        vehicles.append(vehicle_data)
        self.save_data('vehicles', vehicles)
        return True, "Vehicle added successfully"
    
    def get_vehicles(self):
        """Get all vehicles"""
        return self.load_data('vehicles')
    
    def get_vehicle_by_plate(self, plate_number):
        """Get vehicle by plate number"""
        vehicles = self.load_data('vehicles')
        for vehicle in vehicles:
            if vehicle['plate_number'] == plate_number:
                return vehicle
        return None
    
    def update_vehicle(self, plate_number, updated_data):
        """Update vehicle information"""
        vehicles = self.load_data('vehicles')
        
        for i, vehicle in enumerate(vehicles):
            if vehicle['plate_number'] == plate_number:
                vehicles[i].update(updated_data)
                vehicles[i]['updated_at'] = datetime.now().isoformat()
                self.save_data('vehicles', vehicles)
                return True, "Vehicle updated successfully"
        
        return False, "Vehicle not found"
    
    def add_maintenance_record(self, maintenance_data):
        """Add a maintenance record"""
        maintenance_records = self.load_data('maintenance')
        
        # Auto-deduct from inventory if items are used
        inventory = self.load_data('inventory')
        
        if maintenance_data.get('oil_changed', False):
            if inventory.get('oil', 0) > 0:
                inventory['oil'] -= 1
            else:
                return False, "Insufficient oil in inventory"
        
        if maintenance_data.get('air_filter_changed', False):
            if inventory.get('air_filter', 0) > 0:
                inventory['air_filter'] -= 1
            else:
                return False, "Insufficient air filters in inventory"
        
        if maintenance_data.get('tires_changed', 0) > 0:
            if inventory.get('tires', 0) >= maintenance_data['tires_changed']:
                inventory['tires'] -= maintenance_data['tires_changed']
            else:
                return False, "Insufficient tires in inventory"
        
        # Save updated inventory
        self.save_data('inventory', inventory)
        
        # Add timestamp and save maintenance record
        maintenance_data['created_at'] = datetime.now().isoformat()
        maintenance_data['id'] = len(maintenance_records) + 1
        
        maintenance_records.append(maintenance_data)
        self.save_data('maintenance', maintenance_records)
        return True, "Maintenance record added successfully"
    
    def get_maintenance_records(self, plate_number=None):
        """Get maintenance records, optionally filtered by plate number"""
        maintenance_records = self.load_data('maintenance')
        
        if plate_number:
            return [record for record in maintenance_records if record['plate_number'] == plate_number]
        
        return maintenance_records
    
    def update_inventory(self, item_type, quantity, operation='add'):
        """Update inventory quantities"""
        inventory = self.load_data('inventory')
        
        if item_type not in inventory:
            inventory[item_type] = 0
        
        if operation == 'add':
            inventory[item_type] += quantity
        elif operation == 'subtract':
            inventory[item_type] = max(0, inventory[item_type] - quantity)
        elif operation == 'set':
            inventory[item_type] = quantity
        
        self.save_data('inventory', inventory)
        return True, f"Inventory updated: {item_type} = {inventory[item_type]}"
    
    def get_inventory(self):
        """Get current inventory levels"""
        return self.load_data('inventory')
    
    def add_permit(self, permit_data):
        """Add a route permit"""
        permits = self.load_data('permits')
        
        # Add timestamp
        permit_data['created_at'] = datetime.now().isoformat()
        permit_data['id'] = len(permits) + 1
        
        permits.append(permit_data)
        self.save_data('permits', permits)
        return True, "Permit added successfully"
    
    def get_permits(self, plate_number=None):
        """Get permits, optionally filtered by plate number"""
        permits = self.load_data('permits')
        
        if plate_number:
            return [permit for permit in permits if permit['plate_number'] == plate_number]
        
        return permits
    
    def add_token_tax(self, tax_data):
        """Add token tax record"""
        tax_records = self.load_data('token_tax')
        
        # Add timestamp
        tax_data['created_at'] = datetime.now().isoformat()
        tax_data['id'] = len(tax_records) + 1
        
        tax_records.append(tax_data)
        self.save_data('token_tax', tax_records)
        return True, "Token tax record added successfully"
    
    def get_token_tax(self, plate_number=None):
        """Get token tax records, optionally filtered by plate number"""
        tax_records = self.load_data('token_tax')
        
        if plate_number:
            return [record for record in tax_records if record['plate_number'] == plate_number]
        
        return tax_records
    
    def get_expiring_permits(self, days_ahead=30):
        """Get permits expiring within specified days"""
        permits = self.load_data('permits')
        expiring = []
        current_date = datetime.now().date()
        
        for permit in permits:
            expire_date = datetime.fromisoformat(permit['expire_date']).date()
            days_to_expire = (expire_date - current_date).days
            
            if days_to_expire <= days_ahead:
                expiring.append(permit)
        
        return expiring
    
    def get_expiring_taxes(self, days_ahead=30):
        """Get token taxes expiring within specified days"""
        tax_records = self.load_data('token_tax')
        expiring = []
        current_date = datetime.now().date()
        
        for tax in tax_records:
            expire_date = datetime.fromisoformat(tax['expire_date']).date()
            days_to_expire = (expire_date - current_date).days
            
            if days_to_expire <= days_ahead:
                expiring.append(tax)
        
        return expiring
    
    def get_maintenance_alerts(self):
        """Get vehicles needing maintenance based on various criteria"""
        vehicles = self.load_data('vehicles')
        maintenance_records = self.load_data('maintenance')
        alerts = []
        
        for vehicle in vehicles:
            plate_number = vehicle['plate_number']
            
            # Get last maintenance for this vehicle
            vehicle_maintenance = [m for m in maintenance_records if m['plate_number'] == plate_number]
            
            if vehicle_maintenance:
                last_maintenance = max(vehicle_maintenance, key=lambda x: x.get('created_at', ''))
                last_date = datetime.fromisoformat(last_maintenance.get('created_at', datetime.now().isoformat()))
                days_since = (datetime.now() - last_date).days
                
                if days_since > 90:  # More than 3 months
                    alerts.append({
                        'plate_number': plate_number,
                        'alert': f'Last maintenance {days_since} days ago',
                        'priority': 'high' if days_since > 180 else 'medium'
                    })
            else:
                alerts.append({
                    'plate_number': plate_number,
                    'alert': 'No maintenance records found',
                    'priority': 'high'
                })
        
        return alerts
    
    def add_load(self, load_data):
        """Add a new load record"""
        loads = self.load_data('loads')
        
        # Generate load number
        load_number = f"LD{len(loads) + 1:06d}"
        load_data['load_number'] = load_number
        load_data['created_at'] = datetime.now().isoformat()
        load_data['id'] = len(loads) + 1
        
        loads.append(load_data)
        self.save_data('loads', loads)
        return True, f"Load {load_number} added successfully"
    
    def get_loads(self, plate_number=None):
        """Get load records, optionally filtered by plate number"""
        loads = self.load_data('loads')
        
        if plate_number:
            return [load for load in loads if load['plate_number'] == plate_number]
        
        return loads
    
    def update_load_status(self, load_number, new_status):
        """Update load status"""
        loads = self.load_data('loads')
        
        for i, load in enumerate(loads):
            if load['load_number'] == load_number:
                loads[i]['status'] = new_status
                loads[i]['updated_at'] = datetime.now().isoformat()
                self.save_data('loads', loads)
                return True, "Load status updated successfully"
        
        return False, "Load not found"
    
    def export_data(self, data_type):
        """Export data to pandas DataFrame for analysis"""
        data = self.load_data(data_type)
        
        if data_type == 'inventory':
            # Convert inventory dict to DataFrame
            return pd.DataFrame([data])
        
        return pd.DataFrame(data)