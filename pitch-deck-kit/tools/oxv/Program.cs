// Validate a .pptx with Microsoft's Open XML SDK (the same schema + semantic
// constraint tables Office's own tooling uses). Usage: oxv <file.pptx> [version]
using System;
using System.Linq;
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Validation;

var path = args[0];
var versions = args.Length > 1
    ? new[] { Enum.Parse<FileFormatVersions>(args[1]) }
    : new[] { FileFormatVersions.Office2007, FileFormatVersions.Office2016, FileFormatVersions.Microsoft365 };
int worst = 0;
using var doc = PresentationDocument.Open(path, false);
foreach (var ver in versions)
{
    var errs = new OpenXmlValidator(ver).Validate(doc).ToList();
    worst = Math.Max(worst, errs.Count);
    Console.WriteLine($"== {ver}: {errs.Count} error(s)");
    foreach (var g in errs.GroupBy(e => (e.Id, e.Description)).Take(40))
    {
        var first = g.First();
        Console.WriteLine($"  [{g.Count()}x] {g.Key.Id}: {g.Key.Description}");
        foreach (var e in g.Take(3))
            Console.WriteLine($"      at {e.Part?.Uri} {e.Path?.XPath}");
    }
}
return worst == 0 ? 0 : 1;
