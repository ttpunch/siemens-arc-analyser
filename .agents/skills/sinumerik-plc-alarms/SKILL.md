---
name: sinumerik-plc-alarms
description: Trace and plan offline SINUMERIK PLC alarm and operating-message integration. Use for FC10, DB2, acknowledgement, machine-specific interlocks and NC stop or restart behavior; verify the actual controller family and PLC basic program.
---

# SINUMERIK PLC alarm tracing

Keep three questions separate: **what the HMI displays, how the condition
clears or is acknowledged, and what machine reaction the PLC or NC commands**.
A fault class or HMI color alone does not prove any motion reaction.

1. Identify the controller family and basic-program version before choosing a
   manual. Keep 810D/840D Powerline and 840D sl tables separate. For relevant
   840D sl projects, consult Siemens' [PLC Function Manual](https://cache.industry.siemens.com/dl/files/981/109777981/att_1014298/v1/840Dsl_plc_fct_man_1219_en-US.pdf),
   sections 8.3 and 16.18, using the edition matching the installed version.
2. Trace the existing alarm path in the project: condition writer → OEM alarm
   buffer (if present) → copy or direct writes to DB2 → FC10 → message number
   and HMI text. Check the startup FB1 `ExtendAlMsg` setting, DB2 layout and,
   for extended user-alarm configuration, DB5 where applicable. Locate the
   actual FC10 call, its `ToUserIF` value and acknowledgment operand (names
   such as `Quit` or `Ackn` depend on version). Check scan order and copies
   that can overwrite a direct bit write. Never infer a free alarm number
   from a placeholder name.
3. Trace the reaction independently. For applicable channel/axis groups,
   `ToUserIF` controls transfer of configured reactions; the OEM may instead
   write its own PLC/NC interface signals. Do not change this global option
   just to add one user alarm. Verify actual machine axes and spindle roles
   from project code and matching NC configuration; avoid generic axis lists.
   Trace each relevant stop/hold request to its final NC destination and
   separately trace start inhibit and restart. A tag named `Cycle_Stop` or an
   NC start disable does not prove an active cycle stops.
4. For an authorized draft, preserve existing interlocks. Specify the input
   polarity, time qualification, output and startup behavior. For a continuous
   low-level delay, check that recovery resets the timer, separate short low
   episodes do not accumulate, and startup resets the timer as specified for
   its implementation. Distinguish an active condition from alarm
   acknowledgment or an intentional restart latch. Verify the input and
   affected equipment against the actual circuit before choosing reaction scope.
5. Keep verification offline. Review held-low, short-low, recovery, restart,
   acknowledgment and scan-order behavior. Build in an isolated project copy
   only within the requested scope. Label drafts, unresolved mappings and
   checks still to run. Do not alter safety logic or treat a process fault as
   an emergency stop without a separate approved engineering design.

Report the source network and address chain, the evidence for each reaction,
and what still needs to be verified. No machine addresses, alarm slots or axis
counts carry over from one project to another.
