

// // --- Data Translators ---
// function expandData(data) {
//     return {
//         "Full_Name": data.n || "",
//         "Job_Title": data.t || "",
//         "Contact_Info": data.c || "",
//         "Professional_Summary": data.sm || "",
//         "Skills": data.sk || [],
//         "Work_Experience": (data.ex || []).map(e => ({
//             "Company": e.c || "",
//             "Role": e.r || "",
//             "Duration_and_Location": e.d || "",
//             "Responsibilities": e.b || []
//         })),
//         "Education": (data.ed || []).map(e => ({
//             "Degree": e.g || "",
//             "Institution": e.s || "",
//             "Year": e.y || ""
//         })),
//         "Achievements": data.ach || []
//     };
// }

// function compactData(data) {
//     return {
//         "n": data.Full_Name || "",
//         "t": data.Job_Title || "",
//         "c": data.Contact_Info || "",
//         "sm": data.Professional_Summary || "",
//         "sk": data.Skills || [],
//         "ex": (data.Work_Experience || []).map(e => ({
//             "c": e.Company || "",
//             "r": e.Role || "",
//             "d": e.Duration_and_Location || "",
//             "b": e.Responsibilities || []
//         })),
//         "ed": (data.Education || []).map(e => ({
//             "g": e.Degree || "",
//             "s": e.Institution || "",
//             "y": e.Year || ""
//         })),
//         "ach": data.Achievements || []
//     };
// }

// // --- Safely parse the editor JSON ---
// function getEditorJSON() {
//     try {
//         return JSON.parse(document.getElementById('json_editor').value);
//     } catch (err) {
//         alert('Your JSON contains a syntax error. Please fix it before clicking suggestions.');
//         return null;
//     }
// }

// // --- Setup Interactive UI ---
// function renderSuggestions(mskills, sbullets) {
//     const aiContainer = document.getElementById('ai_suggestions');
//     const skillsPanel = document.getElementById('skills_panel');
//     const bulletsPanel = document.getElementById('bullets_panel');
//     const skillsContainer = document.getElementById('skills_container');
//     const bulletsContainer = document.getElementById('bullets_container');
    
//     skillsContainer.innerHTML = '';
//     bulletsContainer.innerHTML = '';
//     let hasSuggestions = false;

//     // Render Skills
//     if (mskills && mskills.length > 0) {
//         hasSuggestions = true;
//         skillsPanel.classList.remove('hidden');
//         mskills.forEach(skill => {
//             const btn = document.createElement('div');
//             btn.className = 'chip';
//             btn.innerText = "+ " + skill;
            
//             btn.addEventListener('click', function() {
//                 const data = getEditorJSON();
//                 if (!data) return;

//                 const isActive = this.classList.contains('active');
//                 if (!isActive) {
//                     if (!data.Skills) data.Skills = [];
//                     if (!data.Skills.includes(skill)) data.Skills.push(skill);
//                     this.classList.add('active');
//                 } else {
//                     if (data.Skills) data.Skills = data.Skills.filter(s => s !== skill);
//                     this.classList.remove('active');
//                 }
//                 document.getElementById('json_editor').value = JSON.stringify(data, null, 4);
//             });
//             skillsContainer.appendChild(btn);
//         });
//     } else {
//         skillsPanel.classList.add('hidden');
//     }

//     // Render Bullets
//     if (sbullets && sbullets.length > 0) {
//         hasSuggestions = true;
//         bulletsPanel.classList.remove('hidden');
//         sbullets.forEach(item => {
//             if(!item.b || item.b.length === 0) return;
            
//             const targetCompany = item.c;
//             item.b.forEach(bullet => {
//                 const btn = document.createElement('div');
//                 btn.className = 'bullet-chip';
                
//                 const compSpan = document.createElement('span');
//                 compSpan.className = 'bullet-company';
//                 compSpan.innerText = targetCompany ? `📍 Add to: ${targetCompany}` : '📍 Add to Experience';
                
//                 const textSpan = document.createElement('span');
//                 textSpan.innerText = "+ " + bullet;
                
//                 btn.appendChild(compSpan);
//                 btn.appendChild(textSpan);

//                 btn.addEventListener('click', function() {
//                     const data = getEditorJSON();
//                     if (!data) return;

//                     const isActive = this.classList.contains('active');
//                     let targetExpIndex = 0; 
                    
//                     if (data.Work_Experience && targetCompany) {
//                         const foundIndex = data.Work_Experience.findIndex(w => 
//                             w.Company.toLowerCase().includes(targetCompany.toLowerCase()) || 
//                             targetCompany.toLowerCase().includes(w.Company.toLowerCase())
//                         );
//                         if (foundIndex !== -1) targetExpIndex = foundIndex;
//                     }

//                     if (!data.Work_Experience || data.Work_Experience.length === 0) {
//                         alert("No work experience block found in JSON to add bullet to.");
//                         return;
//                     }

//                     if (!isActive) {
//                         if (!data.Work_Experience[targetExpIndex].Responsibilities) {
//                             data.Work_Experience[targetExpIndex].Responsibilities = [];
//                         }
//                         data.Work_Experience[targetExpIndex].Responsibilities.push(bullet);
//                         this.classList.add('active');
//                     } else {
//                         if (data.Work_Experience[targetExpIndex].Responsibilities) {
//                             data.Work_Experience[targetExpIndex].Responsibilities = 
//                                 data.Work_Experience[targetExpIndex].Responsibilities.filter(b => b !== bullet);
//                         }
//                         this.classList.remove('active');
//                     }
                    
//                     document.getElementById('json_editor').value = JSON.stringify(data, null, 4);
//                 });
                
//                 bulletsContainer.appendChild(btn);
//             });
//         });
//     } else {
//         bulletsPanel.classList.add('hidden');
//     }

//     if(hasSuggestions) {
//         aiContainer.classList.remove('hidden');
//     } else {
//         aiContainer.classList.add('hidden');
//     }
// }

// // --- Step 1: Submit to Gemini ---
// document.getElementById('draftForm').addEventListener('submit', async (e) => {
//     e.preventDefault();
//     const btn = document.getElementById('btnDraft');
//     const originalText = btn.innerText;
//     btn.innerHTML = `<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Analyzing & Writing...`;
//     btn.disabled = true;

//     // Using FormData directly supports file uploads automatically
//     const formData = new FormData(e.target);
    
//     try {
//         const response = await fetch('/api/draft', {
//             method: 'POST',
//             body: formData
//         });

//         if (!response.ok) {
//             const errorData = await response.json();
//             throw new Error(errorData.error || `Server responded with status ${response.status}`);
//         }

//         const result = await response.json();
        
//         const readableJSON = expandData(result.draft);
//         document.getElementById('json_editor').value = JSON.stringify(readableJSON, null, 4);
        
//         renderSuggestions(result.draft.ms, result.draft.sb);

//         const step2 = document.getElementById('step2');
//         step2.classList.remove('hidden');
//         step2.scrollIntoView({ behavior: 'smooth' });
//     } catch (err) {
//         alert(`Generation failed:\n${err.message}`);
//         console.error(err);
//     } finally {
//         btn.innerText = originalText;
//         btn.disabled = false;
//     }
// });

// // --- Step 2: Confirm and Generate PDF ---
// document.getElementById('btnConfirm').addEventListener('click', async () => {
//     const btn = document.getElementById('btnConfirm');
//     const originalText = btn.innerText;
//     btn.innerHTML = `Compiling PDF...`;
//     btn.disabled = true;

//     const company_name = document.getElementById('company_name').value;
//     const email_to = document.getElementById('email_to').value;
    
//     const frontendData = getEditorJSON();
//     if (!frontendData) {
//         btn.innerText = originalText;
//         btn.disabled = false;
//         return;
//     }
    
//     const backendData = compactData(frontendData);

//     try {
//         const payload = {
//             resume_data: backendData,
//             company_name: company_name,
//             email_to: email_to || null
//         };

//         const response = await fetch('/api/confirm', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify(payload)
//         });

//         if (!response.ok) {
//             throw new Error('Server encountered an error while building the PDF.');
//         }

//         if (email_to) {
//             const result = await response.json();
//             alert('Resume sent successfully to ' + result.email);
//         } else {
//             const blob = await response.blob();
//             const url = window.URL.createObjectURL(blob);
//             const a = document.createElement('a');
//             a.style.display = 'none';
//             a.href = url;
            
//             const contentDisposition = response.headers.get('Content-Disposition');
//             let filename = `resume_${company_name.replace(/\s+/g, '_')}.pdf`;
//             if (contentDisposition && contentDisposition.includes('filename=')) {
//                 filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
//             }
            
//             a.download = filename;
//             document.body.appendChild(a);
//             a.click();
//             window.URL.revokeObjectURL(url);
//         }
//     } catch (err) {
//         alert('Failed to generate PDF. Check console for details.');
//         console.error(err);
//     } finally {
//         btn.innerText = originalText;
//         btn.disabled = false;
//     }
// });

// --- Data Translators ---
function expandData(data) {
    return {
        "Full_Name": data.n || "",
        "Job_Title": data.t || "",
        "Contact_Info": data.c || "",
        "Professional_Summary": data.sm || "",
        "Skills": data.sk || [],
        "Work_Experience": (data.ex || []).map(e => ({
            "Company": e.c || "",
            "Role": e.r || "",
            "Duration_and_Location": e.d || "",
            "Responsibilities": e.b || []
        })),
        "Education": (data.ed || []).map(e => ({
            "Degree": e.g || "",
            "Institution": e.s || "",
            "Year": e.y || ""
        })),
        "Achievements": data.ach || []
    };
}

function compactData(data) {
    return {
        "n": data.Full_Name || "",
        "t": data.Job_Title || "",
        "c": data.Contact_Info || "",
        "sm": data.Professional_Summary || "",
        "sk": data.Skills || [],
        "ex": (data.Work_Experience || []).map(e => ({
            "c": e.Company || "",
            "r": e.Role || "",
            "d": e.Duration_and_Location || "",
            "b": e.Responsibilities || []
        })),
        "ed": (data.Education || []).map(e => ({
            "g": e.Degree || "",
            "s": e.Institution || "",
            "y": e.Year || ""
        })),
        "ach": data.Achievements || []
    };
}

// --- Safely parse the editor JSON ---
function getEditorJSON() {
    try {
        return JSON.parse(document.getElementById('json_editor').value);
    } catch (err) {
        alert('Your JSON contains a syntax error. Please fix it before clicking suggestions.');
        return null;
    }
}

// --- Setup Interactive UI ---
function renderSuggestions(mskills, sbullets) {
    const aiContainer = document.getElementById('ai_suggestions');
    const skillsPanel = document.getElementById('skills_panel');
    const bulletsPanel = document.getElementById('bullets_panel');
    const skillsContainer = document.getElementById('skills_container');
    const bulletsContainer = document.getElementById('bullets_container');
    
    skillsContainer.innerHTML = '';
    bulletsContainer.innerHTML = '';
    let hasSuggestions = false;

    // Render Skills
    if (mskills && mskills.length > 0) {
        hasSuggestions = true;
        skillsPanel.classList.remove('hidden');
        mskills.forEach(skill => {
            const btn = document.createElement('div');
            btn.className = 'chip';
            btn.innerText = "+ " + skill;
            
            btn.addEventListener('click', function() {
                const data = getEditorJSON();
                if (!data) return;

                const isActive = this.classList.contains('active');
                if (!isActive) {
                    if (!data.Skills) data.Skills = [];
                    if (!data.Skills.includes(skill)) data.Skills.push(skill);
                    this.classList.add('active');
                } else {
                    if (data.Skills) data.Skills = data.Skills.filter(s => s !== skill);
                    this.classList.remove('active');
                }
                document.getElementById('json_editor').value = JSON.stringify(data, null, 4);
            });
            skillsContainer.appendChild(btn);
        });
    } else {
        skillsPanel.classList.add('hidden');
    }

    // Render Bullets
    if (sbullets && sbullets.length > 0) {
        hasSuggestions = true;
        bulletsPanel.classList.remove('hidden');
        sbullets.forEach(item => {
            if(!item.b || item.b.length === 0) return;
            
            const targetCompany = item.c;
            item.b.forEach(bullet => {
                const btn = document.createElement('div');
                btn.className = 'bullet-chip';
                
                const compSpan = document.createElement('span');
                compSpan.className = 'bullet-company';
                compSpan.innerText = targetCompany ? `📍 Add to: ${targetCompany}` : '📍 Add to Experience';
                
                const textSpan = document.createElement('span');
                textSpan.innerText = "+ " + bullet;
                
                btn.appendChild(compSpan);
                btn.appendChild(textSpan);

                btn.addEventListener('click', function() {
                    const data = getEditorJSON();
                    if (!data) return;

                    const isActive = this.classList.contains('active');
                    let targetExpIndex = 0; 
                    
                    if (data.Work_Experience && targetCompany) {
                        const foundIndex = data.Work_Experience.findIndex(w => 
                            w.Company.toLowerCase().includes(targetCompany.toLowerCase()) || 
                            targetCompany.toLowerCase().includes(w.Company.toLowerCase())
                        );
                        if (foundIndex !== -1) targetExpIndex = foundIndex;
                    }

                    if (!data.Work_Experience || data.Work_Experience.length === 0) {
                        alert("No work experience block found in JSON to add bullet to.");
                        return;
                    }

                    if (!isActive) {
                        if (!data.Work_Experience[targetExpIndex].Responsibilities) {
                            data.Work_Experience[targetExpIndex].Responsibilities = [];
                        }
                        data.Work_Experience[targetExpIndex].Responsibilities.push(bullet);
                        this.classList.add('active');
                    } else {
                        if (data.Work_Experience[targetExpIndex].Responsibilities) {
                            data.Work_Experience[targetExpIndex].Responsibilities = 
                                data.Work_Experience[targetExpIndex].Responsibilities.filter(b => b !== bullet);
                        }
                        this.classList.remove('active');
                    }
                    
                    document.getElementById('json_editor').value = JSON.stringify(data, null, 4);
                });
                
                bulletsContainer.appendChild(btn);
            });
        });
    } else {
        bulletsPanel.classList.add('hidden');
    }

    if(hasSuggestions) {
        aiContainer.classList.remove('hidden');
    } else {
        aiContainer.classList.add('hidden');
    }
}

// --- Step 1: Submit to Gemini (UPDATED WITH HYBRID ENCRYPTION) ---
document.getElementById('draftForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btnDraft');
    const originalText = btn.innerText;
    btn.innerHTML = `<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Encrypting & Generating...`;
    btn.disabled = true;

    try {
        // 1. Fetch the RSA Public Key from the backend
        const keyResponse = await fetch('/api/public-key');
        if (!keyResponse.ok) throw new Error("Failed to fetch encryption keys from server.");
        const keyData = await keyResponse.json();
        
        // 2. Generate a random AES key and IV
        const aesKey = CryptoJS.lib.WordArray.random(32); // 256-bit key
        const iv = CryptoJS.lib.WordArray.random(16);     // 128-bit IV
        
        // 3. Encrypt the AES key and IV using the RSA Public Key
        const crypt = new JSEncrypt();
        crypt.setPublicKey(keyData.public_key);
        
        const encryptedAesKey = crypt.encrypt(CryptoJS.enc.Base64.stringify(aesKey));
        const encryptedIv = crypt.encrypt(CryptoJS.enc.Base64.stringify(iv));

        if (!encryptedAesKey || !encryptedIv) {
            throw new Error("RSA Encryption failed. Key might be too large.");
        }

        // 4. Gather the form fields into a JSON object
        const rawForm = new FormData(e.target);
        const payloadObject = {
            gemini_key: rawForm.get('gemini_key') || "",
            gemini_model: rawForm.get('gemini_model') || "",
            company_name: rawForm.get('company_name') || "",
            years_exp: rawForm.get('years_exp') || "",
            job_description: rawForm.get('job_description') || "",
            resume_text: rawForm.get('resume_text') || ""
        };

        // 5. Encrypt the entire payload object using the AES key
        const jsonPayload = JSON.stringify(payloadObject);
        const encryptedPayload = CryptoJS.AES.encrypt(jsonPayload, aesKey, {
            iv: iv,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
        }).toString();

        // 6. Construct the secure form data
        const secureFormData = new FormData();
        secureFormData.append('encrypted_key', encryptedAesKey);
        secureFormData.append('encrypted_iv', encryptedIv);
        secureFormData.append('encrypted_payload', encryptedPayload);

        // Append the raw PDF file (Browser JS struggles to encrypt files efficiently)
        const rPdf = rawForm.get('resume_pdf');
        if (rPdf && rPdf.size > 0) {
            secureFormData.append('resume_pdf', rPdf);
        }

        // 7. Send the encrypted package to the backend
        const response = await fetch('/api/draft', {
            method: 'POST',
            body: secureFormData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server responded with status ${response.status}`);
        }

        const result = await response.json();
        
        // Process response payload
        const readableJSON = expandData(result.draft);
        document.getElementById('json_editor').value = JSON.stringify(readableJSON, null, 4);
        
        renderSuggestions(result.draft.ms, result.draft.sb);

        const step2 = document.getElementById('step2');
        step2.classList.remove('hidden');
        step2.scrollIntoView({ behavior: 'smooth' });

    } catch (err) {
        alert(`Generation failed:\n${err.message}`);
        console.error(err);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
});

// --- Step 2: Confirm and Generate PDF ---
// document.getElementById('btnConfirm').addEventListener('click', async () => {
//     const btn = document.getElementById('btnConfirm');
//     const originalText = btn.innerText;
//     btn.innerHTML = `Compiling PDF...`;
//     btn.disabled = true;

//     const company_name = document.getElementById('company_name').value;
//     const email_to = document.getElementById('email_to') ? document.getElementById('email_to').value : null;
    
//     const frontendData = getEditorJSON();
//     if (!frontendData) {
//         btn.innerText = originalText;
//         btn.disabled = false;
//         return;
//     }
    
//     const backendData = compactData(frontendData);

//     try {
//         const payload = {
//             resume_data: backendData,
//             company_name: company_name,
//             email_to: email_to || null
//         };

//         const response = await fetch('/api/confirm', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify(payload)
//         });

//         if (!response.ok) {
//             throw new Error('Server encountered an error while building the PDF.');
//         }

//         if (email_to) {
//             const result = await response.json();
//             alert('Resume sent successfully to ' + result.email);
//         } else {
//             const blob = await response.blob();
//             const url = window.URL.createObjectURL(blob);
//             const a = document.createElement('a');
//             a.style.display = 'none';
//             a.href = url;
            
//             const contentDisposition = response.headers.get('Content-Disposition');
//             let filename = `resume_${company_name.replace(/\s+/g, '_')}.pdf`;
//             if (contentDisposition && contentDisposition.includes('filename=')) {
//                 filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
//             }
            
//             a.download = filename;
//             document.body.appendChild(a);
//             a.click();
//             window.URL.revokeObjectURL(url);
//         }
//     } catch (err) {
//         alert('Failed to generate PDF. Check console for details.');
//         console.error(err);
//     } finally {
//         btn.innerText = originalText;
//         btn.disabled = false;
//     }
// });

// --- Step 2: Confirm and Generate PDF (UPDATED WITH ENCRYPTION) ---
document.getElementById('btnConfirm').addEventListener('click', async () => {
    const btn = document.getElementById('btnConfirm');
    const originalText = btn.innerText;
    btn.innerHTML = `Encrypting & Compiling PDF...`;
    btn.disabled = true;

    const company_name = document.getElementById('company_name').value;
    const email_to = document.getElementById('email_to') ? document.getElementById('email_to').value : null;
    
    const frontendData = getEditorJSON();
    if (!frontendData) {
        btn.innerText = originalText;
        btn.disabled = false;
        return;
    }
    
    const backendData = compactData(frontendData);

    try {
        // 1. Fetch the RSA Public Key from the backend
        const keyResponse = await fetch('/api/public-key');
        if (!keyResponse.ok) throw new Error("Failed to fetch encryption keys.");
        const keyData = await keyResponse.json();
        
        // 2. Generate a random AES key and IV
        const aesKey = CryptoJS.lib.WordArray.random(32); 
        const iv = CryptoJS.lib.WordArray.random(16);     
        
        // 3. Encrypt the AES key and IV using the RSA Public Key
        const crypt = new JSEncrypt();
        crypt.setPublicKey(keyData.public_key);
        
        const encryptedAesKey = crypt.encrypt(CryptoJS.enc.Base64.stringify(aesKey));
        const encryptedIv = crypt.encrypt(CryptoJS.enc.Base64.stringify(iv));

        if (!encryptedAesKey || !encryptedIv) {
            throw new Error("RSA Encryption failed.");
        }

        // 4. Create the raw payload object
        const rawPayload = {
            resume_data: backendData,
            company_name: company_name,
            email_to: email_to || null
        };

        // 5. Encrypt the payload object using AES
        const jsonPayload = JSON.stringify(rawPayload);
        const encryptedPayload = CryptoJS.AES.encrypt(jsonPayload, aesKey, {
            iv: iv,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
        }).toString();

        // 6. Construct the secure JSON body
        const securePayload = {
            encrypted_key: encryptedAesKey,
            encrypted_iv: encryptedIv,
            encrypted_payload: encryptedPayload
        };

        // 7. Send to backend
        const response = await fetch('/api/confirm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(securePayload)
        });

        if (!response.ok) {
            throw new Error('Server encountered an error while building the PDF.');
        }

        // Handle the generated PDF response
        if (email_to) {
            const result = await response.json();
            alert('Resume sent successfully to ' + result.email);
        } else {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `resume_${company_name.replace(/\s+/g, '_')}.pdf`;
            if (contentDisposition && contentDisposition.includes('filename=')) {
                filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        }
    } catch (err) {
        alert('Failed to generate PDF. Check console for details.');
        console.error(err);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
});