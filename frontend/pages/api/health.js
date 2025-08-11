export default function ApiHealth(req, res) {
  res.status(200).json({ status: 'ok' })
}
