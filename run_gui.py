#!/usr/bin/env python3
"""
Pure GUI version of Battery Tester
This version doesn't require terminal and shows all messages in dialog boxes
"""

import pandas as pd
import os
import sys
from tkinter import Tk, filedialog, messagebox
import traceback

# Import our utility functions
try:
    from utils import extract_origin_csv
except ImportError:
    # If we can't import utils, show an error
    root = Tk()
    root.withdraw()
    messagebox.showerror("Error", "Cannot find utils.py file. Make sure it's in the same directory.")
    sys.exit(1)

def main():
    # Create root window but hide it
    root = Tk()
    root.withdraw()
    
    try:
        # Show welcome message
        messagebox.showinfo("Battery Tester", "Welcome to Battery Tester!\n\nClick OK to select your input file.")
        
        # Select input file
        fpath = filedialog.askopenfilename(
            title="Select Input File", 
            filetypes=[("All Files", "*.*"), ("CSV Files", "*.csv"), ("Excel Files", "*.xls;*.xlsx")]
        )
        
        if not fpath:
            messagebox.showwarning("Cancelled", "No input file selected. Application will exit.")
            return
        
        # Show processing message
        messagebox.showinfo("Processing", f"Processing file: {os.path.basename(fpath)}\n\nClick OK to continue...")
        
        # Process the file
        try:
            rows, steps = extract_origin_csv(fpath)
        except Exception as e:
            messagebox.showerror("Processing Error", f"Error processing file:\n\n{str(e)}\n\nPlease check if this is a valid battery tester file.")
            return
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        df.columns = ["System Time", "Step Time", "V", "I", "T", "R", "P", "mAh", "Wh", "Total Time", "Step name"]
        df["System Time"] = df["System Time"].apply(lambda s: pd.to_datetime(s, format="%y/%m/%d %H:%M:%S"))
        df[["V", "I", "T", "R", "P", "mAh", "Wh"]] = df[["V", "I", "T", "R", "P", "mAh", "Wh"]].astype(dtype=float)
        
        filename_head = os.path.basename(fpath).split(".")[0]
        
        # Select output folder
        messagebox.showinfo("Save Files", "Now choose where to save the processed files.")
        folder_path = filedialog.askdirectory(title="Select Folder to Save Files")
        
        if not folder_path:
            messagebox.showwarning("Cancelled", "No output folder selected. Application will exit.")
            return
        
        # Save detail file
        detail_file_path = os.path.join(folder_path, f"{filename_head}_detail.csv")
        df.to_csv(detail_file_path, index=False)
        
        # Save step file
        step_df = df.loc[steps]
        step_file_path = os.path.join(folder_path, f"{filename_head}_step.csv")
        step_df.to_csv(step_file_path, index=False)
        
        # Show success message
        success_msg = f"Processing completed successfully!\n\n"
        success_msg += f"Files saved:\n"
        success_msg += f"• {os.path.basename(detail_file_path)}\n"
        success_msg += f"• {os.path.basename(step_file_path)}\n\n"
        success_msg += f"Location: {folder_path}"
        
        messagebox.showinfo("Success", success_msg)
        
    except Exception as e:
        # Show detailed error message
        error_msg = f"An unexpected error occurred:\n\n{str(e)}\n\n"
        error_msg += "Technical details:\n" + traceback.format_exc()
        messagebox.showerror("Error", error_msg)
    
    finally:
        root.destroy()

if __name__ == "__main__":
    main()