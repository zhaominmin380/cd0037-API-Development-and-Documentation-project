from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    with app.app_context():
        db.create_all()
    
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categoties():
        categories = Category.query.all()
        
        if not categories:
            abort(404)
            
        return jsonify({
            'success':True,
            'categories':{c.id:c.type for c in categories}
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    #paginate func
    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = page * QUESTIONS_PER_PAGE
        return [q.format() for q in selection[start:end]]
    
    #route: /question?page
    @app.route('/questions')
    def get_request_questions():
        questions = Question.query.order_by(Question.id).all()
        
        if not questions:
            abort(404)
            
        questions_per_page = paginate_questions(request, questions)
        
        if len(questions_per_page) == 0:
            abort(404)
            
        categories = Category.query.all()
        return jsonify({
            'success':True,
            'questions':questions_per_page,
            'total_questions':len(questions),
            'categories':{c.id: c.type for c in categories},
            'current_category':None
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        
        if not question:
            abort(404)
        try:
            question.delete()
            return jsonify({
                'success':True,
            })
        except:
            abort(422)
            
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        
        if not body:
            abort(400)
            
        search_term = body.get('searchTerm', None)
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_diff = body.get('difficulty', None)
        new_category = body.get('category', None)
        if search_term:
            results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            return jsonify({
                'success': True,
                'questions': [q.format() for q in results],
                'total_questions': len(results),
                'current_category': None
            })
        
        if not (new_question and new_answer and new_diff and new_category):
            abort(400)
            
        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_diff)
            question.insert()
            return jsonify({
                'success':True
            })
        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:cat_id>/questions')
    def questions_by_categories(cat_id):
        question = Question.query.filter_by(category=cat_id).all()
        
        if not question:
            abort(404)
        
        return jsonify({
            'success': True,
            'questions': [q.format() for q in question],
            'total_questions': len(question),
            'current_category': cat_id
        })
    
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def quiz_question():
        body = request.get_json()
        
        if not body:
            abort(400)
            
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)
        
        try:
            if quiz_category['id'] == 0:
                questions = Question.query.all()

            else:
                questions = Question.query.filter_by(category=quiz_category['id']).all()
        except:
            abort(422)
            
        possible_questions = [q for q in questions if q.id not in previous_questions]
        
        if possible_questions:
            question = random.choice(possible_questions)
            return jsonify({
                'success':True,
                'question':question.format()
            })
        else:
            return jsonify({
                'success':True,
                'question':None
            })
        
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 404, 'message': 'resource not found'}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({'success': False, 'error': 422, 'message': 'unprocessable'}), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False, 'error': 400, 'message': 'bad request'}), 400
    
    return app

