const API_URL = "http://localhost:8000/review";

  async function runReview(){
    const name = document.getElementById('name').value.trim();
    const resumeText = document.getElementById('resume').value.trim();
    const errorBanner = document.getElementById('errorBanner');
    const btn = document.getElementById('submitBtn');
    const loading = document.getElementById('loading');
    const resultEmpty = document.getElementById('resultEmpty');
    const gaugeWrap = document.getElementById('gaugeWrap');

    errorBanner.style.display = 'none';

    if(!resumeText){
      errorBanner.textContent = "Paste in the resume text before running a review.";
      errorBanner.style.display = 'block';
      return;
    }

    btn.disabled = true;
    resultEmpty.style.display = 'none';
    gaugeWrap.classList.remove('active');
    loading.classList.add('active');

    try{
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name || "Unnamed candidate", resume_text: resumeText })
      });

      if(!res.ok){
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Request failed with status ${res.status}`);
      }

      const data = await res.json();
      showResult(data.score, data.feedback);

    } catch(err){
      loading.classList.remove('active');
      resultEmpty.style.display = 'block';
      errorBanner.textContent = "Could not get a review. " +
        "Make sure backend.py is running on localhost:8000. Details: " + err.message;
      errorBanner.style.display = 'block';
    } finally{
      btn.disabled = false;
    }
  }

  function showResult(score, feedback){
    const loading = document.getElementById('loading');
    const gaugeWrap = document.getElementById('gaugeWrap');
    const scoreNumber = document.getElementById('scoreNumber');
    const feedbackBox = document.getElementById('feedbackBox');
    const arc = document.getElementById('gaugeArc');
    const needle = document.getElementById('needle');

    loading.classList.remove('active');
    gaugeWrap.classList.add('active');

    scoreNumber.textContent = score;
    feedbackBox.textContent = feedback;

    let color = getComputedStyle(document.documentElement).getPropertyValue('--bad');
    if(score >= 70) color = getComputedStyle(document.documentElement).getPropertyValue('--good');
    else if(score >= 40) color = getComputedStyle(document.documentElement).getPropertyValue('--mid');
    arc.style.stroke = color;
    scoreNumber.style.color = color;

    const circumference = 283;
    const offset = circumference - (circumference * (score/100));
    arc.style.strokeDashoffset = offset;

    const angle = -90 + (180 * (score/100));
    needle.style.transform = `rotate(${angle}deg)`;
  }