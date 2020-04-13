using Microsoft.AspNetCore.Mvc;
namespace ColourAPI.Controllers
{
   public class AccountController : Controller
    {
        [HttpGet]
        public IActionResult Register()
        {
            return View();
        }
    }}