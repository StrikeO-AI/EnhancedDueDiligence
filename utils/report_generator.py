def generate_report(data, template):
    """Generate ECDD report using provided data and template."""
    try:
        report = template.format(
            analyst_name=data['analyst_name'],
            position=data['position'],
            date=data['date'],
            case_number=data['case_number'],
            user_id=data['user_id'],
            customer_name=data['customer_name'],
            is_pep=data['is_pep'],
            is_sanctioned=data['is_sanctioned'],
            transaction_analysis=data['transaction_analysis'],
            behavioral_analysis=data['behavioral_analysis']
        )
        return report
    except Exception as e:
        raise Exception(f"Error generating report: {str(e)}")

def validate_data(data):
    """Validate required fields in the data."""
    required_fields = [
        'analyst_name', 'position', 'date', 'case_number',
        'user_id', 'customer_name'
    ]
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return True
