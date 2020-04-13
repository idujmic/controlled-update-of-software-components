using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using ColourAPI.Models;

namespace ColourAPI.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ValuesController : ControllerBase
    {
        private readonly ColourContext _context;
        public ValuesController(ColourContext context)
        {
            _context = context;
        }
        // GET api/values
        [HttpGet]
        public ActionResult<IEnumerable<Colour>> GetCoulourItems()
        {
            return _context.ColourItems;
        }

        [HttpGet("{name}")]
        public ActionResult<Colour> GetColourByName(string name) 
        {

            return _context.ColourItems.Where(c => c.ColourName.ToLower() == name.ToLower()).First();

        }       
        [HttpPost]
        public async Task<ActionResult<Colour>> PostTodoItem(string name)
        {
            var newColour = new Colour(){ColourName = name};
            _context.ColourItems.Add(newColour);
            await _context.SaveChangesAsync();
            return CreatedAtAction(nameof(GetColourByName), new { name = name }, newColour);
        }
        [HttpDelete("{name}")]
        public async Task<ActionResult<Colour>> DeleteTodoItem(string name)
        {
            var Colour =  _context.ColourItems.Where(c => c.ColourName.ToLower() == name.ToLower()).First();
            if (Colour == null)
            {
                return NotFound();
            }

            _context.ColourItems.Remove(Colour);
            await _context.SaveChangesAsync();

            return Colour;
        }

    }
}
