import test from 'node:test';
import assert from 'node:assert/strict';
import {requestTextDownload,copyText} from '../browser-export.js';

function browser({blocked=false,supported=true}={}) {
  const calls=[],anchor={hidden:false,click(){calls.push('click');if(blocked)throw Error('Download denied');},remove(){calls.push('remove');}};
  if(supported)anchor.download='';
  const env={Blob,document:{createElement:()=>anchor,body:{append:()=>calls.push('append')}},
    URL:{createObjectURL(blob){calls.push(blob);return 'blob:local';},revokeObjectURL(url){calls.push(url);}},
    setTimeout(fn,delay){calls.push(delay);fn();}};
  return {calls,anchor,env};
}

test('missing or blocked download capability falls back without throwing or claiming success',()=>{
  assert.equal(requestTextDownload('текст','draft.txt',{}),false);
  assert.equal(requestTextDownload('текст','draft.txt',browser({supported:false}).env),false);
  const fixture=browser({blocked:true});assert.equal(requestTextDownload('текст','draft.txt',fixture.env),false);
  assert.ok(fixture.calls.includes('remove'));assert.ok(fixture.calls.includes('blob:local'));
});

test('download request keeps exact JSON and TXT content, attaches anchor, and defers URL revocation',async()=>{
  const text='  D1\n24 В · №7 <script> & "запит"  ';
  for(const name of ['draft.txt','state.json']){
    const fixture=browser();assert.equal(requestTextDownload(text,name,fixture.env),true);
    assert.equal(fixture.anchor.download,name);
    const blob=fixture.calls.find(x=>x instanceof Blob);
    const bytes=new Uint8Array(await blob.arrayBuffer());
    assert.equal(new TextDecoder().decode(bytes),text);
    assert.equal(bytes[0],name.endsWith('.txt')?0xef:0x20);
    assert.ok(fixture.calls.indexOf('append')<fixture.calls.indexOf('click'));
    assert.ok(fixture.calls.includes(60000));
  }
});

test('clipboard absence, rejected permission and throwing accessor return an explicit fallback result',async()=>{
  assert.equal(await copyText('x',{}),false);
  assert.equal(await copyText('x',{navigator:{clipboard:{writeText:async()=>{throw Error('Denied');}}}}),false);
  assert.equal(await copyText('x',{get navigator(){throw Error('Blocked');}}),false);
  let actual;
  assert.equal(await copyText('  D1\n', {navigator:{clipboard:{writeText:async text=>{actual=text;}}}}),true);
  assert.equal(actual,'  D1\n');
});
