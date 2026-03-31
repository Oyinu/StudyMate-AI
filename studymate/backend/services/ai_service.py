import os
import json
import random

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "DEMO")
USE_DEMO = GEMINI_API_KEY == "DEMO" or not GEMINI_API_KEY


# ─── DEMO MODE QUESTIONS ────────────────────────────────────────────────────
DEMO_MCQ = [
    {
        "question": "What is the primary purpose of an operating system?",
        "options": ["A. To manage hardware and software resources", "B. To connect to the internet", "C. To run antivirus software", "D. To display graphics"],
        "answer": "A"
    },
    {
        "question": "Which data structure operates on a Last-In-First-Out (LIFO) principle?",
        "options": ["A. Queue", "B. Linked List", "C. Stack", "D. Tree"],
        "answer": "C"
    },
    {
        "question": "What does CPU stand for?",
        "options": ["A. Central Process Unit", "B. Central Processing Unit", "C. Core Processing Unit", "D. Central Program Utility"],
        "answer": "B"
    },
    {
        "question": "In networking, what does HTTP stand for?",
        "options": ["A. HyperText Transfer Protocol", "B. High Transfer Text Protocol", "C. Hyperlink Text Transfer Process", "D. Host Transfer Text Program"],
        "answer": "A"
    },
    {
        "question": "Which of the following is NOT a programming paradigm?",
        "options": ["A. Object-Oriented", "B. Functional", "C. Sequential Binary", "D. Procedural"],
        "answer": "C"
    },
    {
        "question": "What is the time complexity of binary search?",
        "options": ["A. O(n)", "B. O(n²)", "C. O(log n)", "D. O(1)"],
        "answer": "C"
    },
    {
        "question": "Which SQL command is used to retrieve data from a database?",
        "options": ["A. GET", "B. FETCH", "C. SELECT", "D. RETRIEVE"],
        "answer": "C"
    },
    {
        "question": "What does RAM stand for?",
        "options": ["A. Read Access Memory", "B. Random Access Memory", "C. Rapid Action Module", "D. Read And Modify"],
        "answer": "B"
    },
    {
        "question": "Which layer of the OSI model handles routing between networks?",
        "options": ["A. Data Link Layer", "B. Transport Layer", "C. Network Layer", "D. Session Layer"],
        "answer": "C"
    },
    {
        "question": "What is encapsulation in object-oriented programming?",
        "options": [
            "A. Hiding internal details and exposing only necessary functionality",
            "B. Creating multiple classes from one parent class",
            "C. Running the same method with different parameters",
            "D. Connecting two unrelated classes together"
        ],
        "answer": "A"
    },
    {
        "question": "Which sorting algorithm has the best average-case time complexity?",
        "options": ["A. Bubble Sort", "B. Insertion Sort", "C. Quick Sort", "D. Selection Sort"],
        "answer": "C"
    },
    {
        "question": "In HTML, which tag is used to create a hyperlink?",
        "options": ["A. <link>", "B. <href>", "C. <url>", "D. <a>"],
        "answer": "D"
    },
    {
        "question": "What is the function of a compiler?",
        "options": [
            "A. It executes code line by line",
            "B. It translates high-level source code into machine code",
            "C. It manages computer memory",
            "D. It connects hardware to software"
        ],
        "answer": "B"
    },
    {
        "question": "Which protocol is used to send emails?",
        "options": ["A. FTP", "B. HTTP", "C. SMTP", "D. SSH"],
        "answer": "C"
    },
    {
        "question": "What is a foreign key in a relational database?",
        "options": [
            "A. A key imported from another database system",
            "B. A field that uniquely identifies every row in a table",
            "C. A field that references the primary key of another table",
            "D. An encrypted security key for database access"
        ],
        "answer": "C"
    },
    {
        "question": "What does CSS stand for?",
        "options": ["A. Cascading Style Sheets", "B. Computer Style System", "C. Creative Styling Script", "D. Central Style Syntax"],
        "answer": "A"
    },
    {
        "question": "In Python, what is a list comprehension?",
        "options": [
            "A. A way to document a list",
            "B. A concise way to create lists based on existing iterables",
            "C. A method to sort lists automatically",
            "D. A class for managing lists"
        ],
        "answer": "B"
    },
    {
        "question": "What is the purpose of a firewall in network security?",
        "options": [
            "A. To speed up internet connections",
            "B. To monitor and control incoming and outgoing network traffic",
            "C. To encrypt all data stored on a computer",
            "D. To back up important files automatically"
        ],
        "answer": "B"
    },
    {
        "question": "Which data structure uses a First-In-First-Out (FIFO) approach?",
        "options": ["A. Stack", "B. Queue", "C. Heap", "D. Graph"],
        "answer": "B"
    },
    {
        "question": "What does API stand for?",
        "options": [
            "A. Application Programming Interface",
            "B. Automated Program Integration",
            "C. Advanced Processing Interface",
            "D. Application Process Interaction"
        ],
        "answer": "A"
    }
]

DEMO_THEORY = [
    {
        "question": "Explain the difference between a process and a thread in an operating system.",
        "model_answer": "A process is an independent program in execution with its own memory space, resources, and system state. A thread is a unit of execution within a process — multiple threads can share the same memory space and resources of their parent process. Processes are heavier and more isolated, while threads are lighter and enable concurrent execution within the same application."
    },
    {
        "question": "Describe the four pillars of Object-Oriented Programming (OOP).",
        "model_answer": "The four pillars are: (1) Encapsulation — bundling data and methods together and restricting direct access to internal state. (2) Abstraction — hiding complex implementation details and showing only essential features. (3) Inheritance — allowing a class to derive properties and behaviours from a parent class. (4) Polymorphism — enabling objects of different types to be treated as instances of a common type, with methods behaving differently based on the actual object."
    },
    {
        "question": "What is the difference between symmetric and asymmetric encryption?",
        "model_answer": "Symmetric encryption uses the same key for both encryption and decryption. It is fast and efficient but requires secure key sharing. AES is a common symmetric algorithm. Asymmetric encryption uses a public-private key pair — data encrypted with the public key can only be decrypted with the corresponding private key. It is slower but solves the key distribution problem. RSA is a common asymmetric algorithm. HTTPS combines both: asymmetric encryption for key exchange, then symmetric encryption for data transfer."
    },
    {
        "question": "Explain what normalisation is in database design and why it is important.",
        "model_answer": "Normalisation is the process of organising a relational database to reduce data redundancy and improve data integrity. It involves decomposing tables into smaller, well-structured tables and defining relationships between them. The main normal forms are 1NF (eliminate repeating groups), 2NF (remove partial dependencies), and 3NF (remove transitive dependencies). Normalisation is important because it prevents data anomalies (insertion, update, and deletion anomalies), saves storage space, and makes the database easier to maintain."
    },
    {
        "question": "What is the OSI model and what are its seven layers?",
        "model_answer": "The OSI (Open Systems Interconnection) model is a conceptual framework that standardises the functions of a communication system into seven layers. From bottom to top: (1) Physical — transmits raw bits over a physical medium. (2) Data Link — handles error detection and MAC addressing. (3) Network — manages logical addressing and routing (IP). (4) Transport — ensures end-to-end communication and reliability (TCP/UDP). (5) Session — manages sessions between applications. (6) Presentation — handles data formatting, encryption, and compression. (7) Application — the layer closest to the user, providing network services to applications (HTTP, FTP, SMTP)."
    },
    {
        "question": "Explain the concept of recursion and give an example of when it is used.",
        "model_answer": "Recursion is a programming technique where a function calls itself to solve a problem by breaking it into smaller subproblems of the same type. Every recursive function needs a base case (termination condition) and a recursive case. Example: calculating the factorial of a number — factorial(n) = n * factorial(n-1), with factorial(0) = 1 as the base case. Recursion is commonly used in tree traversal, binary search, merge sort, and solving problems like the Tower of Hanoi."
    },
    {
        "question": "What is the difference between TCP and UDP protocols?",
        "model_answer": "TCP (Transmission Control Protocol) is connection-oriented, meaning it establishes a connection before transmitting data via a three-way handshake. It guarantees delivery, ordering, and error checking, making it reliable but slower. It is used for web browsing (HTTP/HTTPS), email, and file transfers. UDP (User Datagram Protocol) is connectionless — it sends data without establishing a connection and does not guarantee delivery or ordering. It is faster and used for real-time applications like video streaming, online gaming, and DNS queries where speed is more important than reliability."
    },
    {
        "question": "Describe what version control is and why it is important in software development.",
        "model_answer": "Version control is a system that tracks and manages changes to source code over time. It allows multiple developers to collaborate on the same codebase simultaneously, maintains a complete history of all changes, and enables reverting to previous versions if bugs are introduced. Git is the most widely used version control system. Platforms like GitHub and GitLab host remote repositories. Version control is critical because it prevents code loss, enables collaboration without conflicts, supports branching for parallel feature development, and provides accountability through commit history."
    },
    {
        "question": "What is the difference between SQL and NoSQL databases?",
        "model_answer": "SQL databases are relational, store data in structured tables with predefined schemas, and use SQL for querying. They enforce ACID properties (Atomicity, Consistency, Isolation, Durability) and are best for structured data with complex relationships. Examples: MySQL, PostgreSQL. NoSQL databases are non-relational and store data in flexible formats such as documents (MongoDB), key-value pairs (Redis), wide columns (Cassandra), or graphs (Neo4j). They are schema-less, horizontally scalable, and suited for large volumes of unstructured or semi-structured data."
    },
    {
        "question": "Explain what an algorithm is and describe the characteristics of a good algorithm.",
        "model_answer": "An algorithm is a finite, well-defined sequence of instructions designed to solve a specific problem or perform a computation. The characteristics of a good algorithm are: (1) Finiteness — it must terminate after a finite number of steps. (2) Definiteness — each step must be precisely and unambiguously defined. (3) Input — it takes zero or more well-defined inputs. (4) Output — it produces at least one output. (5) Effectiveness — each step must be basic and executable. Additionally, a good algorithm should be efficient in terms of time complexity and space complexity, and correct for all valid inputs."
    }
]


def generate_questions(text: str, difficulty: str, num_mcq: int, num_theory: int) -> dict:
    """
    Generate quiz questions from extracted PDF text.
    Uses Gemini API if key is available, otherwise returns demo questions.
    """
    if USE_DEMO:
        return _generate_demo_questions(num_mcq, num_theory)
    else:
        return _generate_with_gemini(text, difficulty, num_mcq, num_theory)


def _generate_demo_questions(num_mcq: int, num_theory: int) -> dict:
    """Return shuffled demo questions for mock mode."""
    mcq = random.sample(DEMO_MCQ, min(num_mcq, len(DEMO_MCQ)))
    theory = random.sample(DEMO_THEORY, min(num_theory, len(DEMO_THEORY)))
    return {"mcq": mcq, "theory": theory}


def _generate_with_gemini(text: str, difficulty: str, num_mcq: int, num_theory: int) -> dict:
    """Generate questions using Google Gemini API."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Truncate text to avoid token limits
        truncated = text[:8000] if len(text) > 8000 else text

        prompt = f"""You are an expert academic question generator for university-level Computer Science students.

From the lecture note below, generate:
- {num_mcq} multiple choice questions (MCQs) with 4 options each
- {num_theory} theory/short-answer questions
- Difficulty level: {difficulty}

Rules:
- MCQs must have exactly 4 options labeled A, B, C, D
- The answer field must be just the letter: A, B, C, or D
- Theory questions must include a detailed model answer
- Questions must be directly based on the provided text
- Do NOT include question numbers in the question text

Return ONLY valid JSON in exactly this format, no extra text before or after:
{{
  "mcq": [
    {{
      "question": "Question text here?",
      "options": ["A. Option one", "B. Option two", "C. Option three", "D. Option four"],
      "answer": "A"
    }}
  ],
  "theory": [
    {{
      "question": "Theory question here?",
      "model_answer": "Detailed model answer here."
    }}
  ]
}}

Lecture Note:
{truncated}"""

        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        questions = json.loads(raw)

        # Validate structure
        if "mcq" not in questions or "theory" not in questions:
            return _generate_demo_questions(num_mcq, num_theory)

        return questions

    except Exception as e:
        print(f"Gemini API error: {e}")
        return _generate_demo_questions(num_mcq, num_theory)
