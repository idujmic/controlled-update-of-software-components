using Microsoft.AspNetCore.Identity;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using System;


namespace Microsoft.eShopWeb.Infrastructure.Identity
{
    public class AppIdentityDbContextSeed
    {
        public static async Task SeedAsync(UserManager<ApplicationUser> userManager, AppIdentityDbContext userContext)
        {
            var flag = false;
            while(!flag){
                try
                {
                    userContext.Database.Migrate();
                    Console.WriteLine("User uspješna migracija");
                    var defaultUser = new ApplicationUser { UserName = "demouser@microsoft.com", Email = "demouser@microsoft.com" };
                    await userManager.CreateAsync(defaultUser, "Pa55w0rd_1");
                    flag = true;
                }
                catch(Exception ex)
                {

                }
            }

        }
    }
}
