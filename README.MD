## 📦 File Format Compatibility

The `ampla` library parses text-based industrial configuration files into a graph of interconnected Python dictionary nodes. The tool is designed specifically to compare pairs of **`.AAX`**, **`.AA`**, **`.BA`**, or **`.BAX`** files. 

### Supported Combinations

| Left Side | Right Side | Type |
| :--- | :--- | :--- |
| `AAX` | `AAX` | Application Logic |
| `AAX` | `AA` | Application Logic |
| `AA` | `AA` | Application Logic |
| `BAX` | `BAX` | Database Elements |
| `BA` | `BAX` | Database Elements |
| `BA` | `BA` | Database Elements |

> 💡 **Key Features:**
> * **Cross-Source Compatibility:** Code files can originate from different sources (e.g., one from **FCB** and the other from **ONB**).
> * **Auto-Detection:** The program automatically detects the specific file types (`BA`/`BAX`/`AA`/`AAX`).
> * **Multi-Part Stitching:** If a database or logic workspace is split across multiple sequential files, they are automatically merged into a single context.

### Parsing Behaviors
* **Block-Level Evaluation:** Comparisons are executed block by block based on structural topology, rather than raw line-by-line file diffs.
* **Numeric Normalization:** Numeric constants are evaluated by value rather than literal text matching. For example, exponential notation vs flat floats (`D=2.3e-3` and `D=0.0023`) are evaluated as identical and will not trigger a difference warning.
* **XLS Indicators:** Automated Excel sheets are generated via `GenXLSreport(code_before, code_after)`. If variances or errors are caught, the generated file name automatically includes an `*_DIF*` suffix string.

---

## 🛠️ Detailed Class Breakdown

### 1. The Primitive Unit: `class block`
Every individual execution logic module (e.g., `AND`, `OR`, `MOVE`) or database record instance (e.g., an analog input link) maps directly to a `block` instance.

* **Key Attributes:**
  * `self.Address`: Primary unique physical hardware tag string (e.g., `"PC10.3.2.1"`).
  * `self.Name`: Opcode type classification identifier (e.g., `"MOVE"`).
  * `self.Pins`: Internal Python dictionary mapping pin names (`key`) to connections/values (`value`).
  * `self.LineNumber`: Tracking pointer indicating the absolute line index inside the raw source stream.
* **Magic Methods:**
  * `__str__(self)`: Serializes the structural block layout and pin fields into readable terminal prints.
  * `__eq__(self, other)`: Validates deep equality across parameters, descriptions, and functional routes.
  * `__add__(self, values)`: Quick configuration overload syntax to instantly push pin records: `my_block += (":1", "PC10.1.1.1:2")`.
* **Core Method:**
  * `Compare(self, other)`: Evaluates properties pin by pin against another module node to generate explicit delta diagnostics.

### 2. The Project Aggregators: `class AAX` & `class BAX`
These top-level collection drivers ingest, merge, and maintain parsed controller configurations inside runtime memory matrices.

* **`AAX` (Execution Logic Parser):**
  * Processes signal pathways, network tracks, and execution loops.
  * Indices components systematically inside the `self.Blocks` lookup dictionary.
* **`BAX` (Database Instance Parser):**
  * Inherits directly from `AAX`.
  * Overrides the default structural string extraction to isolate tag definitions, signal registers, and physical hardware bounds.
* **Primary API Methods:**
  * `Read()`: Stitches fragmented sequential log distributions (e.g., transitions from `App01.AAX` directly onto `App02.AAX` if an explicit `END` token is absent).
  * `Parse()`: Scans textual arrays to populate parameters and clean multi-line array values.
  * `GetBlock(blkey)`: Retrieves an address instance block or safely defaults to a `NONE` state proxy.
  * `xRef(tag)`: Global lookups producing index listings showing where an individual variable tag is wired.
  * `GetLabels()`: Extracts custom annotations and notes from string lines (e.g., strings matching `N=`).
  * `Compare(other)`: Standard baseline-to-baseline diagnostic reports detecting structural additions, structural deletions, or internal pin variances.

### 3. Binary Layout Extensions: `class AA` & `class BA`
For packed, compressed legacy environments that store information as binary/hex segments rather than exposed flat Unicode text files, these variants leverage a decryption processor utility (`readA`) to transparently decompress and format raw lines before running the string layout engines.

---

## 🎛️ Project Structure Overview

The `Proj` class provides a unified interface for interacting with multiple source programs managed by a single controller workspace.

### Object Hierarchy
