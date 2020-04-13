using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using ColourAPI.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;
using Microsoft.AspNetCore.Identity;

namespace ColourAPI
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        
        public void ConfigureServices(IServiceCollection services)
        {
            var server = Configuration["DBServer"] ?? "ms-sql-server";
            var port = Configuration["DBPort"] ?? "1433";
            var user = Configuration["DBUser"] ?? "SA";
            var password = Configuration["DBPassword"] ?? "Pa55w0rd2019";
            var database = Configuration["Database"] ?? "Colours";
            services.AddDbContext<ColourContext>(options =>
                options.UseSqlServer($"Server={server},{port};Initial Catalog={database};User ID ={user};Password={password}"));
            services.AddMvc().SetCompatibilityVersion(CompatibilityVersion.Version_2_2);
            services.AddIdentity<IdentityUser, IdentityRole>().AddEntityFrameworkStores<ColourContext>();
            services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new OpenApiInfo { Title = "My API", Version = "v1" });
            });

        }

        
        public void Configure(IApplicationBuilder app, IHostingEnvironment env)
        {
            var isConnected = false;
            app.UseMvc();
            while(!isConnected){
                try{
                    PrepDB.PrepPopulation(app);
                    isConnected = true;
                }
                catch(Exception e){
                    System.Threading.Thread.Sleep(2000);
                }
            }
            app.UseSwagger();
            app.UseAuthentication();
            app.UseSwaggerUI(c=> {  
                c.SwaggerEndpoint("/swagger/v1/swagger.json", "post API V1");  
                });

        }
    }
}
