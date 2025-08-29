from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Test, Algorithm, User, db
from sqlalchemy import func, desc
from datetime import datetime, timedelta

tests_bp = Blueprint("tests", __name__)


@tests_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_tests():
    """Get all tests for the current user"""
    try:
        current_user_id = get_jwt_identity()

        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        algorithm_id = request.args.get("algorithm_id", type=int)
        test_type = request.args.get("test_type")
        success_only = request.args.get("success_only", type=bool)

        # Build query
        query = Test.query.filter_by(user_id=current_user_id)

        if algorithm_id:
            query = query.filter_by(algorithm_id=algorithm_id)

        if test_type:
            query = query.filter_by(test_type=test_type)

        if success_only:
            query = query.filter_by(success=True)

        # Order by creation date (newest first)
        query = query.order_by(desc(Test.created_at))

        # Paginate results
        paginated_tests = query.paginate(page=page, per_page=per_page, error_out=False)

        return (
            jsonify(
                {
                    "tests": [test.to_dict() for test in paginated_tests.items],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": paginated_tests.total,
                        "pages": paginated_tests.pages,
                        "has_next": paginated_tests.has_next,
                        "has_prev": paginated_tests.has_prev,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Failed to fetch tests", "details": str(e)}), 500


@tests_bp.route("/<int:test_id>", methods=["GET"])
@jwt_required()
def get_test(test_id):
    """Get specific test details"""
    try:
        current_user_id = get_jwt_identity()
        test = Test.query.filter_by(id=test_id, user_id=current_user_id).first()

        if not test:
            return jsonify({"error": "Test not found"}), 404

        # Include algorithm details
        algorithm = Algorithm.query.get(test.algorithm_id)
        test_data = test.to_dict()
        test_data["algorithm"] = algorithm.to_dict() if algorithm else None

        return jsonify({"test": test_data}), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch test", "details": str(e)}), 500


@tests_bp.route("/<int:test_id>", methods=["DELETE"])
@jwt_required()
def delete_test(test_id):
    """Delete a specific test"""
    try:
        current_user_id = get_jwt_identity()
        test = Test.query.filter_by(id=test_id, user_id=current_user_id).first()

        if not test:
            return jsonify({"error": "Test not found"}), 404

        db.session.delete(test)
        db.session.commit()

        return jsonify({"message": "Test deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete test", "details": str(e)}), 500


@tests_bp.route("/statistics", methods=["GET"])
@jwt_required()
def get_test_statistics():
    """Get test statistics for the current user"""
    try:
        current_user_id = int(get_jwt_identity())
        print(f"DEBUG: Getting statistics for user {current_user_id}")

        # Get date range from query parameters
        days = request.args.get("days", 30, type=int)
        since_date = datetime.utcnow() - timedelta(days=days)

        # Total tests
        total_tests = Test.query.filter_by(user_id=current_user_id).count()
        print(f"DEBUG: Found {total_tests} total tests for user")

        # Recent tests
        recent_tests = Test.query.filter(
            Test.user_id == current_user_id, Test.created_at >= since_date
        ).count()

        # Success rate
        successful_tests = Test.query.filter_by(
            user_id=current_user_id, success=True
        ).count()
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        # Tests by algorithm type
        algorithm_stats = (
            db.session.query(Algorithm.type, func.count(Test.id).label("count"))
            .join(Test, Algorithm.id == Test.algorithm_id)
            .filter(Test.user_id == current_user_id)
            .group_by(Algorithm.type)
            .all()
        )

        # Tests by test type
        test_type_stats = (
            db.session.query(Test.test_type, func.count(Test.id).label("count"))
            .filter(Test.user_id == current_user_id)
            .group_by(Test.test_type)
            .all()
        )

        # Average execution times by algorithm
        execution_time_stats = (
            db.session.query(
                Algorithm.name,
                func.avg(Test.execution_time).label("avg_time"),
                func.min(Test.execution_time).label("min_time"),
                func.max(Test.execution_time).label("max_time"),
            )
            .join(Test, Algorithm.id == Test.algorithm_id)
            .filter(Test.user_id == current_user_id, Test.success == True)
            .group_by(Algorithm.name)
            .all()
        )

        # Recent test activity (daily counts for the last 7 days)
        daily_activity = []
        for i in range(7):
            day_start = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=i)
            day_end = day_start + timedelta(days=1)

            day_count = Test.query.filter(
                Test.user_id == current_user_id,
                Test.created_at >= day_start,
                Test.created_at < day_end,
            ).count()

            daily_activity.append(
                {"date": day_start.strftime("%Y-%m-%d"), "count": day_count}
            )

        return (
            jsonify(
                {
                    "overview": {
                        "total_tests": total_tests,
                        "recent_tests": recent_tests,
                        "success_rate": round(success_rate, 2),
                        "successful_tests": successful_tests,
                        "failed_tests": total_tests - successful_tests,
                    },
                    "algorithm_distribution": [
                        {"type": stat[0], "count": stat[1]} for stat in algorithm_stats
                    ],
                    "test_type_distribution": [
                        {"type": stat[0], "count": stat[1]} for stat in test_type_stats
                    ],
                    "performance_metrics": [
                        {
                            "algorithm": stat[0],
                            "avg_execution_time_ms": (
                                round(float(stat[1]), 2) if stat[1] else 0
                            ),
                            "min_execution_time_ms": (
                                round(float(stat[2]), 2) if stat[2] else 0
                            ),
                            "max_execution_time_ms": (
                                round(float(stat[3]), 2) if stat[3] else 0
                            ),
                        }
                        for stat in execution_time_stats
                    ],
                    "daily_activity": list(
                        reversed(daily_activity)
                    ),  # Most recent first
                    "period_days": days,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"DEBUG: Statistics error: {str(e)}")
        print(f"DEBUG: Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Failed to fetch statistics", "details": str(e)}), 500


@tests_bp.route("/bulk-delete", methods=["POST"])
@jwt_required()
def bulk_delete_tests():
    """Delete multiple tests"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        test_ids = data.get("test_ids", [])
        if not test_ids:
            return jsonify({"error": "No test IDs provided"}), 400

        # Verify all tests belong to the current user
        tests = Test.query.filter(
            Test.id.in_(test_ids), Test.user_id == current_user_id
        ).all()

        if len(tests) != len(test_ids):
            return jsonify({"error": "Some tests not found or access denied"}), 404

        # Delete tests
        for test in tests:
            db.session.delete(test)

        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Successfully deleted {len(tests)} tests",
                    "deleted_count": len(tests),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete tests", "details": str(e)}), 500


@tests_bp.route("/export", methods=["GET"])
@jwt_required()
def export_tests():
    """Export user tests to JSON format"""
    try:
        current_user_id = get_jwt_identity()

        # Get query parameters for filtering
        algorithm_id = request.args.get("algorithm_id", type=int)
        test_type = request.args.get("test_type")
        success_only = request.args.get("success_only", type=bool)
        days = request.args.get("days", type=int)

        # Build query
        query = Test.query.filter_by(user_id=current_user_id)

        if algorithm_id:
            query = query.filter_by(algorithm_id=algorithm_id)

        if test_type:
            query = query.filter_by(test_type=test_type)

        if success_only:
            query = query.filter_by(success=True)

        if days:
            since_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Test.created_at >= since_date)

        tests = query.order_by(desc(Test.created_at)).all()

        # Include algorithm details in export
        export_data = []
        for test in tests:
            algorithm = Algorithm.query.get(test.algorithm_id)
            test_data = test.to_dict()
            test_data["algorithm"] = algorithm.to_dict() if algorithm else None
            export_data.append(test_data)

        # Get user info for export metadata
        user = User.query.get(current_user_id)

        export_result = {
            "metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "exported_by": user.username if user else "Unknown",
                "total_tests": len(export_data),
                "filters_applied": {
                    "algorithm_id": algorithm_id,
                    "test_type": test_type,
                    "success_only": success_only,
                    "days": days,
                },
            },
            "tests": export_data,
        }

        return jsonify(export_result), 200

    except Exception as e:
        return jsonify({"error": "Failed to export tests", "details": str(e)}), 500


@tests_bp.route("/performance-trends", methods=["GET"])
@jwt_required()
def get_performance_trends():
    """Get performance trends over time for algorithms"""
    try:
        current_user_id = get_jwt_identity()
        algorithm_id = request.args.get("algorithm_id", type=int)
        days = request.args.get("days", 7, type=int)

        if not algorithm_id:
            return jsonify({"error": "algorithm_id parameter is required"}), 400

        # Verify algorithm exists and user has tests for it
        algorithm = Algorithm.query.get(algorithm_id)
        if not algorithm:
            return jsonify({"error": "Algorithm not found"}), 404

        since_date = datetime.utcnow() - timedelta(days=days)

        # Get successful tests for the algorithm
        tests = (
            Test.query.filter(
                Test.user_id == current_user_id,
                Test.algorithm_id == algorithm_id,
                Test.success == True,
                Test.created_at >= since_date,
            )
            .order_by(Test.created_at)
            .all()
        )

        if not tests:
            return (
                jsonify(
                    {
                        "algorithm": algorithm.to_dict(),
                        "trends": [],
                        "summary": {
                            "total_tests": 0,
                            "avg_execution_time": 0,
                            "trend_direction": "no_data",
                        },
                    }
                ),
                200,
            )

        # Group tests by day and calculate daily averages
        daily_performance = {}
        for test in tests:
            test_date = test.created_at.strftime("%Y-%m-%d")
            if test_date not in daily_performance:
                daily_performance[test_date] = []
            daily_performance[test_date].append(test.execution_time)

        # Calculate daily averages
        trends = []
        for date, times in daily_performance.items():
            avg_time = sum(times) / len(times)
            trends.append(
                {
                    "date": date,
                    "avg_execution_time_ms": round(avg_time, 2),
                    "test_count": len(times),
                    "min_time": round(min(times), 2),
                    "max_time": round(max(times), 2),
                }
            )

        # Sort by date
        trends.sort(key=lambda x: x["date"])

        # Calculate trend direction
        if len(trends) >= 2:
            first_avg = trends[0]["avg_execution_time_ms"]
            last_avg = trends[-1]["avg_execution_time_ms"]
            if last_avg > first_avg * 1.1:  # More than 10% increase
                trend_direction = "degrading"
            elif last_avg < first_avg * 0.9:  # More than 10% decrease
                trend_direction = "improving"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "insufficient_data"

        # Overall statistics
        all_times = [test.execution_time for test in tests]
        avg_execution_time = sum(all_times) / len(all_times)

        return (
            jsonify(
                {
                    "algorithm": algorithm.to_dict(),
                    "trends": trends,
                    "summary": {
                        "total_tests": len(tests),
                        "avg_execution_time": round(avg_execution_time, 2),
                        "trend_direction": trend_direction,
                        "period_days": days,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify({"error": "Failed to fetch performance trends", "details": str(e)}),
            500,
        )
