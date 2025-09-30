document.addEventListener('DOMContentLoaded', () => {
    const initForm = document.getElementById('init-form');
    const logContainer = document.getElementById('log-container');

    const API_BASE_URL = 'http://127.0.0.1:8000';

    /**
     * Adds a new message to the log container on the page.
     * @param {string} message - The message to display.
     * @param {string} type - The type of message ('success', 'error', 'info').
     */
    function addLog(message, type = 'info') {
        const logEntry = document.createElement('p');
        logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logEntry.style.color = type === 'error' ? '#c0392b' : (type === 'success' ? '#27ae60' : '#2c3e50');
        logContainer.appendChild(logEntry);
        // Scroll to the bottom of the log
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    // --- Initialize Project Logic ---
    initForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        addLog('Initializing new project...', 'info');

        const formData = new FormData(initForm);
        const requestBody = {
            title: formData.get('title'),
            outline_path: formData.get('outline-path'),
            persona_path: formData.get('persona-path') || null,
        };

        try {
            const response = await fetch(`${API_BASE_URL}/projects/init`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Failed to initialize project.');
            }

            addLog(`Project '${requestBody.title}' initialized successfully. Path: ${result.project_path}`, 'success');
            // Auto-fill the project path in the next form for convenience
            document.getElementById('project-path').value = result.project_path;

        } catch (error) {
            addLog(`Error: ${error.message}`, 'error');
        }
    });

    // --- Generate Novel Logic ---
    const generateForm = document.getElementById('generate-form');

    generateForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const projectPath = document.getElementById('project-path').value;

        if (!projectPath) {
            addLog('Error: Project path is required to start generation.', 'error');
            return;
        }

        addLog(`Starting novel generation for project: ${projectPath}...`, 'info');

        try {
            const response = await fetch(`${API_BASE_URL}/projects/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ project_path: projectPath }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Failed to start generation task.');
            }

            addLog(`Task started successfully! Task ID: ${result.task_id}`, 'success');
            addLog('System will now periodically check the task status.', 'info');

            pollTaskStatus(result.task_id);

        } catch (error) {
            addLog(`Error: ${error.message}`, 'error');
        }
    });

    /**
     * Polls the API for the status of a background task.
     * @param {string} taskId - The ID of the task to poll.
     */
    function pollTaskStatus(taskId) {
        const intervalId = setInterval(async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`);
                if (!response.ok) {
                    // Stop polling on server error, but log it
                    addLog(`Error checking task status for ${taskId}. Server responded with ${response.status}.`, 'error');
                    clearInterval(intervalId);
                    return;
                }

                const result = await response.json();

                if (result.status === 'running' || result.status === 'pending') {
                    addLog(`Task ${taskId} is currently: ${result.status}`, 'info');
                } else {
                    // Task is completed or failed, stop polling
                    clearInterval(intervalId);
                    const finalMessage = `Task ${taskId} finished with status: ${result.status}. Result: ${result.result}`;
                    addLog(finalMessage, result.status === 'completed' ? 'success' : 'error');
                }
            } catch (error) {
                // Stop polling on network error
                addLog(`Network error while checking task status: ${error.message}`, 'error');
                clearInterval(intervalId);
            }
        }, 3000); // Poll every 3 seconds
    }
    });

    console.log("InkGen Studio App loaded and ready.");
});