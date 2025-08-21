# Keep-alive endpoint - uyku modunu engeller
@app.route('/ping')
def ping():
    return {'status': 'alive', 'timestamp': get_turkey_time().isoformat()}

# Health check endpoint
@app.route('/health')
def health():
    try:
        # Database bağlantısını test et
        calisan_count = Calisan.query.count()
        kayit_count = DevamKaydi.query.count()
        
        db_type = "PostgreSQL" if os.environ.get('DATABASE_URL') else "SQLite"
        
        return {
            'status': 'healthy',
            'database': db_type,
            'employees': calisan_count,
            'records': kayit_count,
            'timestamp': get_turkey_time().isoformat()
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
