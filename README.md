# GitHub AI Evaluator 🚀

A Full-Stack application that analyzes GitHub user profiles using Artificial Intelligence (Gemini API). The system takes a GitHub username or profile link, fetches the user's public repositories, reads their `README.md` files, and returns a smart AI assessment of the project's complexity, code quality, and clarity.

## 🛠️ Technologies & Stack
* **Frontend:** React, Vite, Tailwind CSS, Lucide Icons
* **Backend:** Python, FastAPI
* **AI & Integration:** Google Gemini API (AI Studio), GitHub API

## 🧠 My Approach to AI (AI-Native Workflow)
In this project, I aimed to use AI not just as a product feature, but as a full partner in the development process:
* **Gemini Web Interface:** Used for architectural brainstorming, logic planning, and solving complex bugs.
* **Gemini VS Code Agent:** Served as an in-editor Copilot for writing boilerplate code, generating functions, and quick debugging.
* **Google AI Studio (API):** The core engine powering the repository evaluations.

## 🚧 Core Challenge & Architecture Decisions
**The Challenge:** Handling Google Gemini's Free Tier Rate Limits (`429 RESOURCE_EXHAUSTED` errors). Initially, sending multiple repositories to the API simultaneously caused the server to crash or return errors due to quota limits.

**The Solution:** Instead of taking the easy route (upgrading to a paid tier), I solved this at the architecture level to ensure a resilient application:
1. **Smart Batching:** I refactored the logic to combine up to 5 repositories into a single API prompt. I specifically limited the batch size to 5 to maintain the quality of the LLM's responses, preventing context overload and AI "hallucinations" or shallow answers.
2. **Retry & Delay Mechanism:** Added a fallback mechanism with a 3-second delay (`asyncio.sleep`) between retries to ensure server stability under heavy load.
3. **Graceful Error Handling:** Handled edge cases seamlessly on the frontend (e.g., displaying a friendly UI state for a `404 User Not Found` instead of crashing, and handling repos without a README).

## 🔮 Future Work
If I had another week to work on this project, I would add:
* **Caching & Database:** Storing previous evaluation results in a database to save API calls and reduce wait times for previously searched users.
* **Extended Testing:** Writing comprehensive unit tests and handling more edge cases.
* **SaaS UI/UX:** Elevating the frontend design and user experience to a full SaaS product level.
* **Deep Code Analysis:** Expanding the API integration to analyze actual source code files in the repositories, rather than just the READMEs.

## 💻 Setup & Installation Instructions

**Prerequisites:**
* Node.js installed
* Python 3.x installed

### Backend Setup
1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend