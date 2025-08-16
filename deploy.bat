@echo off
echo 🚀 Deploying Agentic AI WebTrials to Vercel
echo ==============================================

echo.
echo [INFO] Starting deployment process...

REM Deploy Frontend
echo.
echo [INFO] Deploying Frontend (Next.js)...
cd frontend

REM Check if there are changes to commit
git diff --quiet
if %errorlevel% neq 0 (
    echo [INFO] Committing frontend changes...
    git add .
    git commit -m "Deploy frontend to Vercel"
    git push origin main
) else (
    echo [INFO] No changes to commit in frontend
)

echo [INFO] Frontend deployment triggered via Git push
echo [INFO] Check Vercel dashboard for deployment status

REM Deploy Backend
echo.
echo [INFO] Deploying Backend (FastAPI)...
cd ..\backend

echo [INFO] Running Vercel deployment...
vercel --prod

echo.
echo [INFO] Deployment completed!
echo.
echo 📋 Next Steps:
echo 1. Set environment variables in Vercel dashboard
echo 2. Test your API endpoints
echo 3. Update frontend to use new backend URL
echo.
echo 🔗 Useful Commands:
echo - Check deployment status: vercel ls
echo - View logs: vercel logs [project-url]
echo - Redeploy: vercel --prod
echo.
echo 📚 Full deployment guide: DEPLOYMENT_GUIDE.md

pause
