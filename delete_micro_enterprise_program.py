#!/usr/bin/env python3
"""
Script to delete the Capacity Building for Micro Enterprises program
"""

from extensions import db
from models import Opportunity
from app import create_app

def delete_micro_enterprise_program():
    app = create_app()
    with app.app_context():
        # Find the program
        program = Opportunity.query.filter_by(title="Capacity Building for Micro Enterprises").first()
        
        if program:
            print(f"Found program: {program.title}")
            print(f"ID: {program.id}")
            print(f"Type: {program.type}")
            print(f"Status: {program.status}")
            
            # Delete the program
            db.session.delete(program)
            db.session.commit()
            
            print("✅ Successfully deleted 'Capacity Building for Micro Enterprises' program!")
            
            # Show updated count
            total_opps = Opportunity.query.count()
            published_opps = Opportunity.query.filter_by(status="published").count()
            print(f"Total opportunities remaining: {total_opps}")
            print(f"Published opportunities remaining: {published_opps}")
            
        else:
            print("Program 'Capacity Building for Micro Enterprises' not found in database.")
            
            # Show all programs with 'micro' or 'capacity' in title
            similar_programs = Opportunity.query.filter(
                db.or_(
                    Opportunity.title.ilike('%micro%'),
                    Opportunity.title.ilike('%capacity%')
                )
            ).all()
            
            if similar_programs:
                print("Found similar programs:")
                for prog in similar_programs:
                    print(f"  - {prog.title} (ID: {prog.id})")
            else:
                print("No similar programs found.")

if __name__ == "__main__":
    delete_micro_enterprise_program()