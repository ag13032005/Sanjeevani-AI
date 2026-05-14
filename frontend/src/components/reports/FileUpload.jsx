export default function FileUpload({ file, setFile }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm text-gray-400">Upload MRI / CT / Report File</span>
      <input
        type="file"
        accept=".jpg,.jpeg,.png,.pdf"
        onChange={(event) => setFile(event.target.files?.[0] || null)}
        className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none file:mr-4 file:rounded-xl file:border-0 file:bg-aqua file:px-4 file:py-2 file:font-semibold file:text-slate-950"
      />
      <p className="mt-2 text-xs text-gray-400">Accepted: JPG, PNG, PDF</p>
      {file ? <p className="mt-2 text-sm text-white">Selected: {file.name}</p> : null}
    </label>
  )
}