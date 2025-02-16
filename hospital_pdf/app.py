from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from functions.combinePDF import combine_pdfs
from io import BytesIO
from functions.video_intake import process_surgical_video
from functions.conversation_intake import process_compliance_requirements, test_compliance_processing
from functions.supabase_functions.checklist_update import update_requirement_status
from functions.after_action_report.generate_report import run_report_generation
from functions.preprocessing.analyzePreSurgery import analyze_pre_surgery_compliance, load_and_encode_images, update_supabase
import os

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

@app.route('/generate-report', methods=['POST'])
def generate_report():
    """
    Endpoint to generate post-surgery report
    """
    try:
        output_path = run_report_generation()
        
        if output_path and os.path.exists(output_path):
            return send_file(
                output_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='post_surgery_report.pdf'
            )
        else:
            return jsonify({'error': 'Failed to generate report'}), 500
            
    except Exception as e:
        error_msg = f"Error in generate_report: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/analyze-pre-surgery', methods=['POST'])
def analyze_pre_surgery():
    """
    Endpoint to analyze pre-surgery images for compliance
    """
    try:
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400

        # Get all images from the request
        images = request.files.getlist('images')
        if not images:
            return jsonify({'error': 'Empty image list'}), 400

        print(f"Received {len(images)} images for analysis")
        
        # Create temporary directory with absolute path
        temp_dir = os.path.abspath("temp_pre_surgery_images")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            print(f"Created temporary directory at: {temp_dir}")
            
        try:
            # Save uploaded images temporarily
            image_paths = []
            for img in images:
                if img.filename:
                    # Sanitize filename
                    safe_filename = os.path.basename(img.filename)
                    temp_path = os.path.join(temp_dir, safe_filename)
                    img.save(temp_path)
                    image_paths.append(temp_path)
                    print(f"Saved image to {temp_path}")

            # Process the images
            encoded_images = load_and_encode_images(temp_dir)
            if not encoded_images:
                return jsonify({'error': 'Failed to process images'}), 500

            # Analyze the images
            analysis = analyze_pre_surgery_compliance(encoded_images)
            if not analysis:
                return jsonify({'error': 'Failed to analyze images'}), 500

            # Update Supabase with results
            update_result = update_supabase(analysis)
            if not update_result:
                return jsonify({'error': 'Failed to update database'}), 500

            return jsonify({
                'success': True,
                'analysis': analysis
            })

        finally:
            # Clean up temporary files
            for path in image_paths:
                if os.path.exists(path):
                    os.remove(path)
                    print(f"Removed temporary file: {path}")
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
                print(f"Removed temporary directory: {temp_dir}")

    except Exception as e:
        error_msg = f"Error in analyze_pre_surgery: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)