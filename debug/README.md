# Debug Folder

This folder contains **debugging screenshots** from the most recent scraper run.

## 📸 Screenshot Types

The Playwright scraper automatically takes screenshots during login:

| Screenshot | When Taken | Purpose |
|------------|------------|---------|
| `before_next.png` | Before clicking "Next" button | Verify username was entered |
| `after_next.png` | After clicking "Next" button | Check password page loaded |
| `verification_required.png` | If Twitter asks for verification | Debug verification challenges |
| `password_field_error.png` | If password field has issues | Debug password entry problems |
| `login_error.png` | If login fails | Diagnose login failures |

## 🔄 Auto-Cleanup

Screenshots are **automatically cleaned up** at the start of each run, so this folder only contains screenshots from the **most recent run**.

## 🎯 Usage

If the scraper has login issues:
1. Check the screenshots in this folder
2. They show exactly what the browser saw
3. Use them to diagnose issues like:
   - Wrong login page
   - Verification challenges
   - CAPTCHA requirements
   - Password field not found

## 🔒 Privacy

Screenshots may contain sensitive information:
- ✅ This folder is **excluded from git** (see `.gitignore`)
- ✅ Only kept locally on your machine
- ✅ Auto-cleaned on each run (no old screenshots accumulate)

