// Read-only TIA Portal Openness probe (compiled on the Windows host with csc.exe).
//   tiaprobe.exe                 -> running Portal processes + open project paths (no attach, no dialog)
//   tiaprobe.exe --blocks        -> attach to the running Portal and enumerate PLC blocks (needs the
//                                   one-time Openness trust dialog on the operator's screen)
// Nothing here writes to a project, compiles, downloads or goes online with a CPU.
using System;
using System.Collections.Generic;
using System.Linq;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;

static class TiaProbe
{
    static string Prop(object o, string name)
    {
        if (o == null) return "";
        var pi = o.GetType().GetProperty(name);
        if (pi == null) return "";
        try { var v = pi.GetValue(o, null); return v == null ? "" : v.ToString(); }
        catch { return "?"; }
    }

    static void Main(string[] args)
    {
        string exportDir = null;
        for (int i = 0; i < args.Length; i++)
            if (args[i] == "--export" && i + 1 < args.Length) exportDir = args[i + 1];
        bool wantBlocks = args.Contains("--blocks") || exportDir != null;
        TiaPortalProcess[] procs;
        try { procs = TiaPortal.GetProcesses().ToArray(); }
        catch (Exception e)
        {
            Console.WriteLine("ERROR_GETPROCESSES|" + e.GetType().Name + "|" + e.Message);
            return;
        }

        Console.WriteLine("PROCESS_COUNT|" + procs.Length);
        foreach (var p in procs)
        {
            Console.WriteLine(string.Join("|", new[] {
                "PROCESS",
                Prop(p, "ProcessId"),
                Prop(p, "ProjectPath"),
                Prop(p, "Mode"),
                Prop(p, "StartTime"),
                Prop(p, "Version")
            }));
        }
        if (!wantBlocks) return;

        var target = procs.FirstOrDefault(p => !string.IsNullOrEmpty(Prop(p, "ProjectPath"))) ?? procs.FirstOrDefault();
        if (target == null) { Console.WriteLine("NO_PORTAL_PROCESS"); return; }

        TiaPortal tia = null;
        try
        {
            Console.WriteLine("ATTACHING|" + Prop(target, "ProcessId"));
            tia = target.Attach();
            Console.WriteLine("ATTACHED|" + Prop(tia, "Version"));
        }
        catch (Exception e)
        {
            Console.WriteLine("ATTACH_FAILED|" + e.GetType().Name + "|" + e.Message);
            return;
        }

        try
        {
            foreach (var proj in tia.Projects)
            {
                Console.WriteLine("PROJECT|" + Prop(proj, "Name") + "|" + Prop(proj, "Path"));
                foreach (var dev in proj.Devices)
                    WalkDevice(dev, "", exportDir);
            }
        }
        catch (Exception e)
        {
            Console.WriteLine("ENUM_FAILED|" + e.GetType().Name + "|" + e.Message);
        }
        finally
        {
            try { tia.Dispose(); } catch { }
        }
    }

    static void ExportBlock(PlcBlock b, string plcPath, string root)
    {
        var safePlc = plcPath.Trim('/').Replace("/", "_").Replace(" ", "_");
        var dir = System.IO.Path.Combine(root, safePlc);
        System.IO.Directory.CreateDirectory(dir);
        var tag = Prop(b, "Number") + "_" + Prop(b, "Name");
        foreach (var ch in System.IO.Path.GetInvalidFileNameChars()) tag = tag.Replace(ch, '_');
        var file = System.IO.Path.Combine(dir, tag + ".xml");
        try
        {
            b.Export(new System.IO.FileInfo(file), ExportOptions.WithDefaults);
            Console.WriteLine("EXPORT|ok|" + tag + "|" + file);
        }
        catch (Exception e)
        {
            Console.WriteLine("EXPORT|fail|" + tag + "|" + e.GetType().Name + ": " + e.Message.Replace("|", "/"));
        }
    }

    static void WalkDevice(Device dev, string prefix, string exportDir)
    {
        var name = prefix + "/" + Prop(dev, "Name");
        Console.WriteLine("DEVICE|" + name + "|" + Prop(dev, "TypeIdentifier"));
        foreach (var item in dev.DeviceItems) WalkItem(item, name, exportDir);
    }

    static void WalkItem(DeviceItem item, string prefix, string exportDir)
    {
        var name = prefix + "/" + Prop(item, "Name");
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is PlcSoftware)
        {
            var plc = (PlcSoftware)sc.Software;
            Console.WriteLine("PLC|" + name + "|" + Prop(plc, "Name"));
            WalkGroup(plc.BlockGroup, name, 0, exportDir);
        }
        foreach (var child in item.DeviceItems) WalkItem(child, name, exportDir);
    }

    static void WalkGroup(PlcBlockGroup group, string plcPath, int depth, string exportDir)
    {
        foreach (var b in group.Blocks)
        {
            Console.WriteLine(string.Join("|", new[] {
                "BLOCK",
                plcPath,
                depth.ToString(),
                Prop(group, "Name"),
                b.GetType().Name,                 // OB / FC / FB / GlobalDB / InstanceDB / ...
                Prop(b, "Name"),
                Prop(b, "Number"),
                Prop(b, "ProgrammingLanguage"),
                Prop(b, "HeaderVersion"),
                Prop(b, "MemoryLayout"),
                Prop(b, "IsConsistent"),
                Prop(b, "IsKnowHowProtected")
            }));
            if (exportDir != null) ExportBlock(b, plcPath, exportDir);
        }
        foreach (var sub in group.Groups) WalkGroup(sub, plcPath, depth + 1, exportDir);
    }
}
