using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
namespace ColourAPI.Models
{
    public class ColourContext : IdentityDbContext
    {
        public ColourContext(DbContextOptions<ColourContext> options) : base(options)
        {

        }
        public DbSet<Colour> ColourItems {get; set;}
        
    }
}