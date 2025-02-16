from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from functions.combinePDF import combine_pdfs
from io import BytesIO
from functions.video_intake import process_surgical_video
from functions.conversation_intake import process_compliance_requirements, test_compliance_processing
from functions.supabase_functions.checklist_update import update_requirement_status

app = Flask(__name__)
CORS(app)

@app.route('/process-conversation', methods=['POST'])
def process_conversation():
    """
    Endpoint to process surgical conversation for compliance requirements
    """
    try:
        data = request.get_json()
        
        if not data or 'conversation' not in data:
            return jsonify({'error': 'Conversation text is required'}), 400
            
        conversation_text = data.get('conversation')
        print(f"Received conversation text: {conversation_text[:100]}...") # Debug log
        
        try:
            results = test_compliance_processing(conversation_text)
            print(f"Processing results: {results}") # Debug log
            if results is None:
                return jsonify({'error': 'Processing failed - received None result'}), 500
                
            return results
                
        except Exception as processing_error:
            print(f"Error in compliance processing: {str(processing_error)}") # Debug log
            return jsonify({'error': f'Compliance processing error: {str(processing_error)}'}), 500
            
    except Exception as e:
        error_msg = f"Error in process_conversation: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/update-requirement', methods=['POST', 'OPTIONS'])
def update_requirement():
    """
    Endpoint to update the status of a specific requirement
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json()
        
        if not data or 'requirement' not in data:
            return jsonify({'error': 'Requirement text is required'}), 400
            
        requirement = data.get('requirement')
        print(f"Received update request for requirement: {requirement[:50]}...")
        
        success = update_requirement_status(requirement)
        
        response = jsonify({
            'success': True,
            'message': f'Successfully updated status for: {requirement[:50]}...'
        }) if success else jsonify({
            'success': False,
            'error': f'Failed to update requirement: {requirement[:50]}...'
        }), 404
        
        if isinstance(response, tuple):
            response[0].headers.add('Access-Control-Allow-Origin', '*')
        else:
            response.headers.add('Access-Control-Allow-Origin', '*')
            
        return response
            
    except Exception as e:
        error_msg = f"Error in update_requirement: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)