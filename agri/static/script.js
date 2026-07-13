/**
 * Frontend JavaScript logic for Agricultural Loan Credit Scorer
 * Handles form validation, data collection, API integration, and dynamic UI updates
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const loanForm = document.getElementById('loan-form');
    const resultSection = document.getElementById('result-section');
    const resultDetails = document.getElementById('result-details');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const errorMessage = document.getElementById('error-message');

    // Outputs
    const resStatus = document.getElementById('res-status');
    const resScore = document.getElementById('res-score');
    const resRisk = document.getElementById('res-risk');

    // --- Form Submit Handler ---
    loanForm.addEventListener('submit', (e) => {
        // Allow form to submit naturally to /prediction/ endpoint defined in the HTML form action
        // The form will POST all data to the Django predict view
        console.log('Form submitted to /prediction/');
        // No preventDefault - let the form submit naturally
    });

    // --- Helper Functions ---

    /**
     * Toggles button loading state
     * @param {boolean} isLoading 
     */
    function setLoadingState(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.textContent = 'Analyzing...';
            btnSpinner.classList.remove('hidden');
        } else {
            submitBtn.disabled = false;
            btnText.textContent = 'Predict Loan Approval';
            btnSpinner.classList.add('hidden');
        }
    }

    /**
     * Resets and hides the result card
     */
    function hideResults() {
        resultSection.classList.add('hidden');
        errorMessage.classList.add('hidden');
        resultDetails.style.display = 'flex'; // Reset in case it was hidden by an error
    }

    /**
     * Displays an error message
     * @param {string} msg 
     */
    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
        resultSection.classList.remove('hidden');
        resultDetails.style.display = 'none'; // Hide the result block to show only error
    }

    /**
     * Updates the UI with prediction data and appropriate CSS classes
     * @param {Object} data - Prediction payload
     */
    function displayPrediction(data) {
        // Reset old classes
        resStatus.className = 'result-value';
        resRisk.className = 'result-value';

        // Set Loan Status
        const status = data.status || 'Unknown';
        resStatus.textContent = status;
        if (status === 'Approved') resStatus.classList.add('st-approved');
        else if (status === 'Rejected') resStatus.classList.add('st-rejected');

        // Set Credit Score
        const scoreVal = data.score !== undefined ? data.score : '--';
        resScore.textContent = `${scoreVal}/100`;

        // Set Risk Level
        const risk = data.risk || 'Unknown';
        resRisk.textContent = risk;
        if (risk === 'Low') resRisk.classList.add('rk-low');
        else if (risk === 'Medium') resRisk.classList.add('rk-medium');
        else if (risk === 'High') resRisk.classList.add('rk-high');

        // Reveal the section and scroll smoothly into view
        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Fallback mock logic for hackathon demonstration if backend fails
     */
    function simulateMockPrediction(req) {
        // Simple heuristic for mock demo
        let score = 50;
        
        // Income to Loan Ratio
        if (req.income > req.loanAmount * 2) score += 20;
        else if (req.income > req.loanAmount) score += 10;
        
        // Experience
        if (req.experience > 5) score += 10;
        
        // Credit History
        if (req.creditHistory === 'Good') score += 15;
        else score -= 20;
        
        // Soil / Assets
        if (req.soilQuality >= 7) score += 10;
        if (req.irrigationType === 'Irrigated') score += 5;

        // Cap at 100
        score = Math.min(100, Math.max(0, score));

        // Determine output
        let status = 'Rejected';
        let risk = 'High';

        if (score >= 75) {
            status = 'Approved';
            risk = 'Low';
        } else if (score >= 55) {
            status = 'Approved';
            risk = 'Medium';
        }

        displayPrediction({
            status: status,
            score: score,
            risk: risk
        });
    }

    // Hide clear results when form gets new input
    loanForm.addEventListener('input', () => {
        if (!resultSection.classList.contains('hidden')) {
            hideResults();
        }
    });

});
