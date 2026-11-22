using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using DotNetSiemensPLCToolBoxLibrary.DataTypes;
using DotNetSiemensPLCToolBoxLibrary.DataTypes.Blocks;
using DotNetSiemensPLCToolBoxLibrary.DataTypes.Projectfolders;
using DotNetSiemensPLCToolBoxLibrary.DataTypes.Projectfolders.Step7V5;
using DotNetSiemensPLCToolBoxLibrary.Projectfiles;

// s7awl: read-only STEP 7 V5 project -> AWL/STL source export via
// DotNetSiemensPLCToolBoxLibrary. Never writes to the project, never connects.
//
//   s7awl <project.s7p|project-folder> [--list] [--block FC67] [--out DIR] [--all]
internal static class Program
{
    private static int Main(string[] args)
    {
        if (args.Length == 0)
        {
            Console.Error.WriteLine("usage: s7awl <project.s7p|folder> [--list] [--block FC67] [--out DIR] [--all]");
            return 2;
        }
        string path = args[0];
        bool list = args.Contains("--list");
        bool all = args.Contains("--all");
        string block = ArgValue(args, "--block");
        string outDir = ArgValue(args, "--out");

        Project prj;
        try
        {
            prj = Projects.LoadProject(path, false);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"load failed: {ex.GetType().Name}: {ex.Message}");
            return 1;
        }

        Console.WriteLine($"project : {prj.ProjectName}  ({prj.ProjectType})");
        Console.WriteLine($"file    : {prj.ProjectFile}");
        Console.WriteLine($"folders : {prj.AllFolders?.Count ?? 0}");

        var progFolders = new List<S7ProgrammFolder>();
        CollectProgFolders(prj.ProjectStructure, progFolders);
        Console.WriteLine($"S7 programs: {progFolders.Count}");

        int written = 0;
        bool probe = args.Contains("--probe");
        foreach (var pf in progFolders)
        {
            var folder = pf.BlocksOfflineFolder;
            if (folder == null) continue;
            var infos = folder.BlockInfos ?? new List<ProjectBlockInfo>();
            Console.WriteLine($"  program '{pf.Name}': {infos.Count} blocks");
            if (probe && infos.Count > 0)
            {
                var t = infos[0].GetType();
                Console.WriteLine($"  probe type: {t.FullName}");
                foreach (var p in t.GetProperties())
                {
                    object v;
                    try { v = p.GetValue(infos[0]); } catch { v = "<err>"; }
                    Console.WriteLine($"    {p.PropertyType.Name,-22} {p.Name} = {v}");
                }
            }
            foreach (var info in infos)
            {
                string label = info is DotNetSiemensPLCToolBoxLibrary.DataTypes.Blocks.Step7V5.S7ProjectBlockInfo s7i
                    ? s7i.BlockName
                    : $"{info.BlockType}{info.Name}";
                if (list)
                {
                    Console.WriteLine($"    {info.BlockType,-4} {info.Name,-10} {(info.IsInstance ? "(instance)" : "")}");
                    continue;
                }
                bool want = all
                    || (!string.IsNullOrEmpty(block)
                        && (Matches(label, block) || Matches(info.Name, block)));
                if (!want) continue;
                try
                {
                    string src = info.GetSourceBlock();
                    if (string.IsNullOrWhiteSpace(src))
                    {
                        Console.WriteLine($"    {label}: no source");
                        continue;
                    }
                    if (!string.IsNullOrEmpty(outDir))
                    {
                        Directory.CreateDirectory(outDir);
                        string f = Path.Combine(outDir, $"{label}.awl");
                        File.WriteAllText(f, src);
                        written++;
                        Console.WriteLine($"    wrote {f} ({src.Split('\n').Length} lines)");
                    }
                    else
                    {
                        Console.WriteLine($"===== {label} =====");
                        Console.WriteLine(src);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"    {label}: {ex.GetType().Name}: {ex.Message}");
                }
            }
        }
        Console.WriteLine($"exported : {written} file(s)");
        return 0;
    }

    private static bool Matches(string a, string b)
    {
        static string Norm(string s) => new string((s ?? "").Where(char.IsLetterOrDigit).ToArray()).ToUpperInvariant();
        return Norm(a) == Norm(b);
    }

    private static void CollectProgFolders(ProjectFolder folder, List<S7ProgrammFolder> acc)
    {
        if (folder == null) return;
        if (folder is S7ProgrammFolder pf) acc.Add(pf);
        if (folder.SubItems == null) return;
        foreach (var child in folder.SubItems) CollectProgFolders(child, acc);
    }

    private static string ArgValue(string[] args, string name)
    {
        int i = Array.IndexOf(args, name);
        return (i >= 0 && i + 1 < args.Length) ? args[i + 1] : "";
    }
}
