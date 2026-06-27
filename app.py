# NomadShare - Flask Web Server
# Handles web requests and file serving

from flask import Flask, render_template, request, redirect, jsonify
from nomadshare_db import NomadShareDB
from config import SUPABASE_URL, SUPABASE_KEY, BOT_USERNAME
from Script import script
import os
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)
db = NomadShareDB(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    """Home page"""
    return jsonify({
        'status': 'online',
        'bot_name': 'NomadShare',
        'version': '1.0.0',
        'message': 'NomadShare - Permanent File Storage Bot'
    })

@app.route('/file/<file_id>')
async def get_file(file_id):
    """Get file by ID"""
    try:
        file_data = await db.get_file(file_id)
        
        if not file_data:
            return jsonify({'error': 'File not found'}), 404
        
        # Increment access count
        await db.increment_access_count(file_id)
        
        return jsonify({
            'file_id': file_data['id'],
            'file_name': file_data['file_name'],
            'file_size': file_data['file_size'],
            'uploaded_by': file_data['uploaded_by'],
            'upload_date': file_data['upload_date'],
            'access_count': file_data['access_count'],
            'is_public': file_data['is_public']
        })
        
    except Exception as e:
        logger.error(f"Error getting file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/link/<short_code>')
async def access_link(short_code):
    """Access file via short link"""
    try:
        link_data = await db.get_link(short_code)
        
        if not link_data:
            return jsonify({'error': 'Link not found'}), 404
        
        if not link_data['is_active']:
            return jsonify({'error': 'Link is inactive'}), 403
        
        file_data = await db.get_file(link_data['file_id'])
        
        if not file_data:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify({
            'file_id': file_data['id'],
            'file_name': file_data['file_name'],
            'file_size': file_data['file_size'],
            'telegram_file_id': file_data['file_id'],
            'bot': f'@{BOT_USERNAME}'
        })
        
    except Exception as e:
        logger.error(f"Error accessing link: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
async def get_stats():
    """Get bot statistics"""
    try:
        stats = await db.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'NomadShare',
        'timestamp': str(os.popen('date').read().strip())
    })

@app.errorhandler(404)
def not_found(error):
    """404 handler"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """500 handler"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
