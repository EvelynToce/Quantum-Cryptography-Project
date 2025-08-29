from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Report, Test, Algorithm, User, db
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_reports():
    """Get all reports for the current user"""
    try:
        current_user_id = get_jwt_identity()

        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        report_type = request.args.get("report_type")

        # Build query
        query = Report.query.filter_by(user_id=current_user_id)

        if report_type:
            query = query.filter_by(report_type=report_type)

        # Order by creation date (newest first)
        query = query.order_by(desc(Report.created_at))

        # Paginate results
        paginated_reports = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        return (
            jsonify(
                {
                    "reports": [report.to_dict() for report in paginated_reports.items],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": paginated_reports.total,
                        "pages": paginated_reports.pages,
                        "has_next": paginated_reports.has_next,
                        "has_prev": paginated_reports.has_prev,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Failed to fetch reports", "details": str(e)}), 500


@reports_bp.route("/<int:report_id>", methods=["GET"])
@jwt_required()
def get_report(report_id):
    """Get specific report details"""
    try:
        current_user_id = get_jwt_identity()
        report = Report.query.filter_by(id=report_id, user_id=current_user_id).first()

        if not report:
            return jsonify({"error": "Report not found"}), 404

        return jsonify({"report": report.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch report", "details": str(e)}), 500


@reports_bp.route("/<int:report_id>", methods=["DELETE"])
@jwt_required()
def delete_report(report_id):
    """Delete a specific report"""
    try:
        current_user_id = get_jwt_identity()
        report = Report.query.filter_by(id=report_id, user_id=current_user_id).first()

        if not report:
            return jsonify({"error": "Report not found"}), 404

        db.session.delete(report)
        db.session.commit()

        return jsonify({"message": "Report deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete report", "details": str(e)}), 500


@reports_bp.route("/generate/performance", methods=["POST"])
@jwt_required()
def generate_performance_report():
    """Generate a performance analysis report"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        algorithm_ids = data.get("algorithm_ids", [])
        days = data.get("days", 30)
        title = data.get(
            "title", f'Performance Report - {datetime.utcnow().strftime("%Y-%m-%d")}'
        )

        if not algorithm_ids:
            return jsonify({"error": "At least one algorithm ID is required"}), 400

        # Verify algorithms exist
        algorithms = Algorithm.query.filter(Algorithm.id.in_(algorithm_ids)).all()
        if len(algorithms) != len(algorithm_ids):
            return jsonify({"error": "Some algorithms not found"}), 404

        since_date = datetime.utcnow() - timedelta(days=days)

        # Collect performance data for each algorithm
        algorithm_performance = []

        for algorithm in algorithms:
            # Get successful tests for this algorithm
            tests = Test.query.filter(
                Test.user_id == current_user_id,
                Test.algorithm_id == algorithm.id,
                Test.success == True,
                Test.created_at >= since_date,
            ).all()

            if tests:
                execution_times = [test.execution_time for test in tests]
                avg_time = sum(execution_times) / len(execution_times)
                min_time = min(execution_times)
                max_time = max(execution_times)

                # Calculate test type distribution
                test_types = {}
                for test in tests:
                    test_types[test.test_type] = test_types.get(test.test_type, 0) + 1

                algorithm_performance.append(
                    {
                        "algorithm": algorithm.to_dict(),
                        "metrics": {
                            "total_tests": len(tests),
                            "avg_execution_time_ms": round(avg_time, 2),
                            "min_execution_time_ms": round(min_time, 2),
                            "max_execution_time_ms": round(max_time, 2),
                            "std_deviation": (
                                round(
                                    (
                                        sum(
                                            (t - avg_time) ** 2 for t in execution_times
                                        )
                                        / len(execution_times)
                                    )
                                    ** 0.5,
                                    2,
                                )
                                if len(execution_times) > 1
                                else 0
                            ),
                        },
                        "test_distribution": test_types,
                    }
                )
            else:
                algorithm_performance.append(
                    {
                        "algorithm": algorithm.to_dict(),
                        "metrics": {
                            "total_tests": 0,
                            "avg_execution_time_ms": 0,
                            "min_execution_time_ms": 0,
                            "max_execution_time_ms": 0,
                            "std_deviation": 0,
                        },
                        "test_distribution": {},
                    }
                )

        # Generate performance ranking
        ranked_algorithms = sorted(
            [alg for alg in algorithm_performance if alg["metrics"]["total_tests"] > 0],
            key=lambda x: x["metrics"]["avg_execution_time_ms"],
        )

        # Generate recommendations
        recommendations = []

        if ranked_algorithms:
            fastest = ranked_algorithms[0]
            recommendations.append(
                f"Best performing algorithm: {fastest['algorithm']['name']} "
                f"with average execution time of {fastest['metrics']['avg_execution_time_ms']}ms"
            )

            if len(ranked_algorithms) > 1:
                slowest = ranked_algorithms[-1]
                recommendations.append(
                    f"Consider optimizing {slowest['algorithm']['name']} "
                    f"as it has the highest average execution time of {slowest['metrics']['avg_execution_time_ms']}ms"
                )

            # Quantum-safe recommendations
            quantum_safe_algos = [
                alg for alg in algorithm_performance if alg["algorithm"]["quantum_safe"]
            ]
            if quantum_safe_algos:
                recommendations.append(
                    f"Found {len(quantum_safe_algos)} quantum-safe algorithms in your tests. "
                    "Consider migrating to post-quantum cryptography for future-proof security."
                )
        else:
            recommendations.append(
                "No test data available for the selected algorithms and time period."
            )

        # Create report content
        report_content = {
            "analysis_period": {
                "days": days,
                "start_date": since_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
            },
            "algorithms_analyzed": len(algorithms),
            "performance_data": algorithm_performance,
            "performance_ranking": ranked_algorithms,
            "summary_statistics": {
                "total_tests": sum(
                    alg["metrics"]["total_tests"] for alg in algorithm_performance
                ),
                "algorithms_with_data": len(
                    [
                        alg
                        for alg in algorithm_performance
                        if alg["metrics"]["total_tests"] > 0
                    ]
                ),
                "quantum_safe_count": len(
                    [
                        alg
                        for alg in algorithm_performance
                        if alg["algorithm"]["quantum_safe"]
                    ]
                ),
            },
        }

        # Generate summary
        summary = (
            f"Performance analysis of {len(algorithms)} algorithms over {days} days. "
        )
        total_tests = sum(
            alg["metrics"]["total_tests"] for alg in algorithm_performance
        )
        summary += f"Total tests analyzed: {total_tests}. "

        if ranked_algorithms:
            best_performer = ranked_algorithms[0]
            summary += f"Best performer: {best_performer['algorithm']['name']} "
            summary += f"({best_performer['metrics']['avg_execution_time_ms']}ms avg)."

        # Create report record
        report = Report(
            user_id=current_user_id,
            title=title,
            report_type="performance",
            content=report_content,
            algorithms_tested=algorithm_ids,
            summary=summary,
            recommendations=". ".join(recommendations),
        )

        db.session.add(report)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Performance report generated successfully",
                    "report": report.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {"error": "Failed to generate performance report", "details": str(e)}
            ),
            500,
        )


@reports_bp.route("/generate/security", methods=["POST"])
@jwt_required()
def generate_security_report():
    """Generate a security analysis report"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        title = data.get(
            "title",
            f'Security Analysis Report - {datetime.utcnow().strftime("%Y-%m-%d")}',
        )

        # Get all algorithms and their test results
        algorithms = Algorithm.query.all()

        # Categorize algorithms
        classical_algorithms = [alg for alg in algorithms if alg.type == "classical"]
        post_quantum_algorithms = [
            alg for alg in algorithms if alg.type == "post-quantum"
        ]

        # Analyze test success rates for each algorithm
        algorithm_security_analysis = []

        for algorithm in algorithms:
            total_tests = Test.query.filter_by(
                user_id=current_user_id, algorithm_id=algorithm.id
            ).count()

            successful_tests = Test.query.filter_by(
                user_id=current_user_id, algorithm_id=algorithm.id, success=True
            ).count()

            success_rate = (
                (successful_tests / total_tests * 100) if total_tests > 0 else 0
            )

            # Security assessment based on algorithm type and success rate
            security_level = "unknown"
            security_notes = []

            if algorithm.quantum_safe:
                if success_rate >= 95:
                    security_level = "high"
                    security_notes.append("Quantum-safe with excellent reliability")
                elif success_rate >= 80:
                    security_level = "medium-high"
                    security_notes.append("Quantum-safe with good reliability")
                else:
                    security_level = "medium"
                    security_notes.append(
                        "Quantum-safe but implementation issues detected"
                    )
            else:
                if success_rate >= 95:
                    security_level = "medium"
                    security_notes.append(
                        "Classical algorithm - vulnerable to quantum attacks"
                    )
                elif success_rate >= 80:
                    security_level = "medium-low"
                    security_notes.append(
                        "Classical algorithm with reliability concerns"
                    )
                else:
                    security_level = "low"
                    security_notes.append(
                        "Classical algorithm with significant implementation issues"
                    )

            # Key size assessment
            if algorithm.category == "RSA":
                if algorithm.key_size >= 4096:
                    security_notes.append("Strong key size for current threats")
                elif algorithm.key_size >= 2048:
                    security_notes.append("Adequate key size but consider upgrading")
                else:
                    security_notes.append("Weak key size - upgrade recommended")
            elif algorithm.category == "AES":
                if algorithm.key_size >= 256:
                    security_notes.append("Strong symmetric key size")
                else:
                    security_notes.append("Consider upgrading to AES-256")

            algorithm_security_analysis.append(
                {
                    "algorithm": algorithm.to_dict(),
                    "test_results": {
                        "total_tests": total_tests,
                        "successful_tests": successful_tests,
                        "success_rate": round(success_rate, 2),
                    },
                    "security_assessment": {
                        "level": security_level,
                        "notes": security_notes,
                        "quantum_safe": algorithm.quantum_safe,
                    },
                }
            )

        # Generate recommendations
        recommendations = []

        # Quantum readiness assessment
        user_pq_tests = (
            Test.query.join(Algorithm)
            .filter(Test.user_id == current_user_id, Algorithm.quantum_safe == True)
            .count()
        )

        user_classical_tests = (
            Test.query.join(Algorithm)
            .filter(Test.user_id == current_user_id, Algorithm.quantum_safe == False)
            .count()
        )

        pq_adoption_rate = (
            (user_pq_tests / (user_pq_tests + user_classical_tests) * 100)
            if (user_pq_tests + user_classical_tests) > 0
            else 0
        )

        if pq_adoption_rate < 25:
            recommendations.append(
                "Low post-quantum cryptography adoption detected. "
                "Start evaluating and migrating to quantum-safe algorithms."
            )
        elif pq_adoption_rate < 50:
            recommendations.append(
                "Moderate post-quantum cryptography adoption. "
                "Accelerate migration to quantum-safe algorithms."
            )
        else:
            recommendations.append(
                "Good post-quantum cryptography adoption. "
                "Continue expanding quantum-safe algorithm usage."
            )

        # Algorithm-specific recommendations
        weak_algorithms = [
            alg
            for alg in algorithm_security_analysis
            if alg["security_assessment"]["level"] in ["low", "medium-low"]
        ]

        if weak_algorithms:
            recommendations.append(
                f"Review {len(weak_algorithms)} algorithms with security concerns: "
                f"{', '.join([alg['algorithm']['name'] for alg in weak_algorithms])}"
            )

        # Create report content
        report_content = {
            "security_overview": {
                "total_algorithms_analyzed": len(algorithms),
                "classical_algorithms": len(classical_algorithms),
                "post_quantum_algorithms": len(post_quantum_algorithms),
                "quantum_readiness_score": round(pq_adoption_rate, 2),
            },
            "algorithm_analysis": algorithm_security_analysis,
            "security_distribution": {
                "high": len(
                    [
                        alg
                        for alg in algorithm_security_analysis
                        if alg["security_assessment"]["level"] == "high"
                    ]
                ),
                "medium-high": len(
                    [
                        alg
                        for alg in algorithm_security_analysis
                        if alg["security_assessment"]["level"] == "medium-high"
                    ]
                ),
                "medium": len(
                    [
                        alg
                        for alg in algorithm_security_analysis
                        if alg["security_assessment"]["level"] == "medium"
                    ]
                ),
                "medium-low": len(
                    [
                        alg
                        for alg in algorithm_security_analysis
                        if alg["security_assessment"]["level"] == "medium-low"
                    ]
                ),
                "low": len(
                    [
                        alg
                        for alg in algorithm_security_analysis
                        if alg["security_assessment"]["level"] == "low"
                    ]
                ),
                "unknown": len(
                    [
                        alg
                        for alg in algorithm_security_analysis
                        if alg["security_assessment"]["level"] == "unknown"
                    ]
                ),
            },
        }

        # Generate summary
        summary = f"Security analysis of {len(algorithms)} cryptographic algorithms. "
        summary += f"Quantum readiness score: {round(pq_adoption_rate, 2)}%. "
        summary += (
            f"Post-quantum algorithms available: {len(post_quantum_algorithms)}. "
        )

        high_security_count = len(
            [
                alg
                for alg in algorithm_security_analysis
                if alg["security_assessment"]["level"] == "high"
            ]
        )
        summary += f"High security algorithms: {high_security_count}."

        # Create report record
        report = Report(
            user_id=current_user_id,
            title=title,
            report_type="security",
            content=report_content,
            algorithms_tested=[alg.id for alg in algorithms],
            summary=summary,
            recommendations=". ".join(recommendations),
        )

        db.session.add(report)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Security report generated successfully",
                    "report": report.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"error": "Failed to generate security report", "details": str(e)}),
            500,
        )


@reports_bp.route("/generate/comparison", methods=["POST"])
@jwt_required()
def generate_comparison_report():
    """Generate a comparison report between algorithms"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        algorithm_ids = data.get("algorithm_ids", [])
        title = data.get(
            "title",
            f'Algorithm Comparison Report - {datetime.utcnow().strftime("%Y-%m-%d")}',
        )
        days = data.get("days", 30)

        if len(algorithm_ids) < 2:
            return (
                jsonify({"error": "At least 2 algorithms required for comparison"}),
                400,
            )

        # Verify algorithms exist
        algorithms = Algorithm.query.filter(Algorithm.id.in_(algorithm_ids)).all()
        if len(algorithms) != len(algorithm_ids):
            return jsonify({"error": "Some algorithms not found"}), 404

        since_date = datetime.utcnow() - timedelta(days=days)

        # Collect comparison data
        comparison_data = []

        for algorithm in algorithms:
            tests = Test.query.filter(
                Test.user_id == current_user_id,
                Test.algorithm_id == algorithm.id,
                Test.created_at >= since_date,
            ).all()

            successful_tests = [test for test in tests if test.success]

            if successful_tests:
                execution_times = [test.execution_time for test in successful_tests]
                avg_time = sum(execution_times) / len(execution_times)

                comparison_data.append(
                    {
                        "algorithm": algorithm.to_dict(),
                        "performance_metrics": {
                            "total_tests": len(tests),
                            "successful_tests": len(successful_tests),
                            "success_rate": (
                                round(len(successful_tests) / len(tests) * 100, 2)
                                if tests
                                else 0
                            ),
                            "avg_execution_time_ms": round(avg_time, 2),
                            "min_execution_time_ms": round(min(execution_times), 2),
                            "max_execution_time_ms": round(max(execution_times), 2),
                        },
                        "security_properties": {
                            "quantum_safe": algorithm.quantum_safe,
                            "key_size": algorithm.key_size,
                            "algorithm_type": algorithm.type,
                            "category": algorithm.category,
                        },
                    }
                )
            else:
                comparison_data.append(
                    {
                        "algorithm": algorithm.to_dict(),
                        "performance_metrics": {
                            "total_tests": len(tests),
                            "successful_tests": 0,
                            "success_rate": 0,
                            "avg_execution_time_ms": 0,
                            "min_execution_time_ms": 0,
                            "max_execution_time_ms": 0,
                        },
                        "security_properties": {
                            "quantum_safe": algorithm.quantum_safe,
                            "key_size": algorithm.key_size,
                            "algorithm_type": algorithm.type,
                            "category": algorithm.category,
                        },
                    }
                )

        # Generate comparison insights
        insights = []

        # Performance comparison
        algorithms_with_data = [
            alg
            for alg in comparison_data
            if alg["performance_metrics"]["successful_tests"] > 0
        ]

        if algorithms_with_data:
            fastest = min(
                algorithms_with_data,
                key=lambda x: x["performance_metrics"]["avg_execution_time_ms"],
            )
            slowest = max(
                algorithms_with_data,
                key=lambda x: x["performance_metrics"]["avg_execution_time_ms"],
            )

            insights.append(
                f"Performance: {fastest['algorithm']['name']} is the fastest "
                f"({fastest['performance_metrics']['avg_execution_time_ms']}ms avg), "
                f"{slowest['algorithm']['name']} is the slowest "
                f"({slowest['performance_metrics']['avg_execution_time_ms']}ms avg)"
            )

            # Reliability comparison
            most_reliable = max(
                algorithms_with_data,
                key=lambda x: x["performance_metrics"]["success_rate"],
            )
            insights.append(
                f"Reliability: {most_reliable['algorithm']['name']} has the highest success rate "
                f"({most_reliable['performance_metrics']['success_rate']}%)"
            )

        # Security comparison
        quantum_safe_algos = [
            alg for alg in comparison_data if alg["security_properties"]["quantum_safe"]
        ]
        classical_algos = [
            alg
            for alg in comparison_data
            if not alg["security_properties"]["quantum_safe"]
        ]

        insights.append(
            f"Security: {len(quantum_safe_algos)} quantum-safe algorithms, "
            f"{len(classical_algos)} classical algorithms"
        )

        # Generate recommendations
        recommendations = []

        if quantum_safe_algos and classical_algos:
            recommendations.append(
                "Consider migrating from classical to quantum-safe algorithms for future-proof security."
            )

        if algorithms_with_data:
            if fastest["security_properties"]["quantum_safe"]:
                recommendations.append(
                    f"Recommended: {fastest['algorithm']['name']} offers both good performance and quantum safety."
                )
            else:
                pq_with_data = [
                    alg
                    for alg in algorithms_with_data
                    if alg["security_properties"]["quantum_safe"]
                ]
                if pq_with_data:
                    best_pq = min(
                        pq_with_data,
                        key=lambda x: x["performance_metrics"]["avg_execution_time_ms"],
                    )
                    recommendations.append(
                        f"For quantum safety, consider {best_pq['algorithm']['name']} "
                        f"({best_pq['performance_metrics']['avg_execution_time_ms']}ms avg)."
                    )

        # Create report content
        report_content = {
            "comparison_parameters": {
                "algorithms_compared": len(algorithms),
                "analysis_period_days": days,
                "start_date": since_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
            },
            "algorithm_comparison": comparison_data,
            "performance_ranking": sorted(
                algorithms_with_data,
                key=lambda x: x["performance_metrics"]["avg_execution_time_ms"],
            ),
            "security_analysis": {
                "quantum_safe_algorithms": len(quantum_safe_algos),
                "classical_algorithms": len(classical_algos),
            },
            "insights": insights,
        }

        # Generate summary
        summary = f"Comparison of {len(algorithms)} algorithms over {days} days. "
        if algorithms_with_data:
            summary += f"Performance leader: {fastest['algorithm']['name']}. "
        summary += (
            f"Quantum-safe algorithms: {len(quantum_safe_algos)}/{len(algorithms)}."
        )

        # Create report record
        report = Report(
            user_id=current_user_id,
            title=title,
            report_type="comparison",
            content=report_content,
            algorithms_tested=algorithm_ids,
            summary=summary,
            recommendations=". ".join(recommendations),
        )

        db.session.add(report)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Comparison report generated successfully",
                    "report": report.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {"error": "Failed to generate comparison report", "details": str(e)}
            ),
            500,
        )


@reports_bp.route("/types", methods=["GET"])
def get_report_types():
    """Get available report types"""
    return (
        jsonify(
            {
                "report_types": [
                    {
                        "type": "performance",
                        "name": "Performance Analysis",
                        "description": "Analyze algorithm execution times and performance metrics",
                    },
                    {
                        "type": "security",
                        "name": "Security Assessment",
                        "description": "Evaluate security properties and quantum readiness",
                    },
                    {
                        "type": "comparison",
                        "name": "Algorithm Comparison",
                        "description": "Compare multiple algorithms across various metrics",
                    },
                ]
            }
        ),
        200,
    )
