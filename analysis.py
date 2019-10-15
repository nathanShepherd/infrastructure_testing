from trex_archiver import collect_archive

def viz_simple_stats(simple_stats):
  for t in simple_stats:
    print(t)
    for tt in simple_stats[t]:
      if t == "Total-tx-bytes":
        tt = str(float(tt.split("bytes")[0]) / 10000000000) + " GB"
      if t == "CpuUtilization":
        tt = tt.split("Gb/core")[0].split("%")
        tt = tt[0] +" % "+ tt[1] + " Gb/core"

      print("\t" + tt)

      if tt in ["0", "1"]:
        for ttt in simple_stats[t][tt]:
          print("\t" + ttt)
          for tttt in simple_stats[t][tt][ttt]:
            print("\t\t" + tttt)

def clean_archive(archive):
  print("***** CLEANED *****")
  for test in archive:
    for t in archive[test]:
      print(t)

      for tt in archive[test][t]:
        if "port" not in tt:
          break
        print('\t' + tt)

if __name__ == "__main__":
        hive = {}
        collect_archive(hive)

        for title in hive:
                print("||| TITLE ||| ::: " + title)
                viz_simple_stats(hive[title])
        clean_archive(hive)
