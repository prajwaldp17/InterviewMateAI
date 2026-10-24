
from history import init_db, save_interview, get_history

# Create the database table
init_db()

# Save a sample interview
save_interview(
    category="HR",
    question="Tell me about yourself.",
    answer="I am a B.Tech Computer Science graduate.",
    feedback="Good introduction. Add your relevant skills and career goal."
)

# Display saved interviews
history = get_history()

print("Total saved interviews:", len(history))

if history:
    print("Latest interview:", history[0])
